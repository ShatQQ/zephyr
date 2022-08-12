/*  NVS: non volatile storage in flash
 *
 * Copyright (c) 2018 Laczen
 *
 * SPDX-License-Identifier: Apache-2.0
 */
#ifndef ZEPHYR_INCLUDE_FS_NVS_H_
#define ZEPHYR_INCLUDE_FS_NVS_H_

#include <sys/types.h>
#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/toolchain.h>
#include <zephyr/devicetree.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Non-volatile Storage
 * @defgroup nvs Non-volatile Storage
 * @ingroup file_system_storage
 * @{
 * @}
 */

/**
 * @brief Non-volatile Storage Data Structures
 * @defgroup nvs_data_structures Non-volatile Storage Data Structures
 * @ingroup nvs
 * @{
 */

/**
 * @brief Non-volatile storage file system operations api.
 * This structure is used to map underling storage operations to the file system.
 */
struct nvs_storage_operations {
	int (*read)(const struct device *dev, off_t offset, void *data, size_t len);
	int (*write)(const struct device *dev, off_t offset, const void *data, size_t len);
	int (*erase)(const struct device *dev, off_t offset, size_t size);
};

/**
 * @brief Storage parameter structure
 * These informations are needed by the nvs from the storage device,
 * so the nvs can work with the parameters.
 */
struct nvs_storage_parameters {
	size_t write_block_size;
	uint8_t erase_value; /* Byte value of erased storage device */
	size_t page_size;
};

/**
 * @brief Non-volatile Storage File system structure
 *
 * @param offset File system offset in flash
 * @param ate_wra Allocation table entry write address. Addresses are stored as uint32_t:
 * high 2 bytes correspond to the sector, low 2 bytes are the offset in the sector
 * @param data_wra Data write address
 * @param sector_size File system is split into sectors, each sector must be multiple of pagesize
 * @param sector_count Number of sectors in the file systems
 * @param ready Flag indicating if the filesystem is initialized
 * @param nvs_lock Mutex
 * @param storage_device Storage device runtime structure
 * @param storage_operations Storage operations api structure
 * @param storage_parameters Memory storage parameters structure
 */
struct nvs_fs {
	off_t offset;
	uint32_t ate_wra;
	uint32_t data_wra;
	uint16_t sector_size;
	uint16_t sector_count;
	bool ready;
	struct k_mutex nvs_lock;
	const struct device *storage_device;
	const struct nvs_storage_operations *storage_operations;
	const struct nvs_storage_parameters *storage_parameters;
#if CONFIG_NVS_LOOKUP_CACHE
	uint32_t lookup_cache[CONFIG_NVS_LOOKUP_CACHE_SIZE];
#endif
};

/**
 * @}
 */

/**
 * @brief Non-volatile Storage APIs
 * @defgroup nvs_high_level_api Non-volatile Storage APIs
 * @ingroup nvs
 * @{
 */

/**
 * @brief nvs_mount
 *
 * Mount a NVS file system onto the flash device specified in @p fs.
 *
 * @param fs Pointer to file system
 * @retval 0 Success
 * @retval -ERRNO errno code if error
 */
int nvs_mount(struct nvs_fs *fs);

/**
 * @brief nvs_clear
 *
 * Clears the NVS file system from flash.
 * @param fs Pointer to file system
 * @retval 0 Success
 * @retval -ERRNO errno code if error
 */
int nvs_clear(struct nvs_fs *fs);

/**
 * @brief nvs_write
 *
 * Write an entry to the file system.
 *
 * @param fs Pointer to file system
 * @param id Id of the entry to be written
 * @param data Pointer to the data to be written
 * @param len Number of bytes to be written
 *
 * @return Number of bytes written. On success, it will be equal to the number of bytes requested
 * to be written. When a rewrite of the same data already stored is attempted, nothing is written
 * to flash, thus 0 is returned. On error, returns negative value of errno.h defined error codes.
 */
ssize_t nvs_write(struct nvs_fs *fs, uint16_t id, const void *data, size_t len);

/**
 * @brief nvs_delete
 *
 * Delete an entry from the file system
 *
 * @param fs Pointer to file system
 * @param id Id of the entry to be deleted
 * @retval 0 Success
 * @retval -ERRNO errno code if error
 */
int nvs_delete(struct nvs_fs *fs, uint16_t id);

/**
 * @brief nvs_read
 *
 * Read an entry from the file system.
 *
 * @param fs Pointer to file system
 * @param id Id of the entry to be read
 * @param data Pointer to data buffer
 * @param len Number of bytes to be read
 *
 * @return Number of bytes read. On success, it will be equal to the number of bytes requested
 * to be read. When the return value is larger than the number of bytes requested to read this
 * indicates not all bytes were read, and more data is available. On error, returns negative
 * value of errno.h defined error codes.
 */
ssize_t nvs_read(struct nvs_fs *fs, uint16_t id, void *data, size_t len);

/**
 * @brief nvs_read_hist
 *
 * Read a history entry from the file system.
 *
 * @param fs Pointer to file system
 * @param id Id of the entry to be read
 * @param data Pointer to data buffer
 * @param len Number of bytes to be read
 * @param cnt History counter: 0: latest entry, 1: one before latest ...
 *
 * @return Number of bytes read. On success, it will be equal to the number of bytes requested
 * to be read. When the return value is larger than the number of bytes requested to read this
 * indicates not all bytes were read, and more data is available. On error, returns negative
 * value of errno.h defined error codes.
 */
ssize_t nvs_read_hist(struct nvs_fs *fs, uint16_t id, void *data, size_t len, uint16_t cnt);

/**
 * @brief nvs_calc_free_space
 *
 * Calculate the available free space in the file system.
 *
 * @param fs Pointer to file system
 *
 * @return Number of bytes free. On success, it will be equal to the number of bytes that can
 * still be written to the file system. Calculating the free space is a time consuming operation,
 * especially on spi flash. On error, returns negative value of errno.h defined error codes.
 */
ssize_t nvs_calc_free_space(struct nvs_fs *fs);

/**
 * @brief nvs_init
 *
 * Initializes a NVS file system in flash.
 *
 * @deprecated Use nvs_mount() instead.
 *
 * @param fs Pointer to file system
 * @param dev_name Pointer to flash device name
 * @retval 0 Success
 * @retval -ERRNO errno code if error
 */
__deprecated static inline int nvs_init(struct nvs_fs *fs, const char *dev_name)
{
	fs->storage_device = device_get_binding(dev_name);
	if (fs->storage_device == NULL) {
		return -ENODEV;
	}

	return nvs_mount(fs);
}

/**
 * Get device pointer for device the area/partition resides on
 *
 * @param label partition node label
 *
 * @return const struct device type pointer
 */
#define NVS_FS_DEFINE(label) \
	DT_NODE_FULL_NAME(DT_GPARENT(DT_NODELABEL(label)))

/**
 * TBD description define for the eeprom
 *
 * @param eeprom_partition_label partition node label for a eeprom partition
 * @param name name of the nvs structure which is created
 *
 * @return const struct device type pointer
 */
#define NVS_EEPROM_DEFINE(eeprom_partition_label, name, s_size, s_count, e_value) 			\
	static inline int nvs_eeprom_erase(const struct device *dev, off_t offset, size_t size)		\
	{												\
		uint8_t data[s_size] = {0U};								\
		memset(data, e_value , size);								\
		return eeprom_write(dev, offset, data, size);						\
	}												\
	static const struct nvs_storage_operations nvs_eeprom_##name##_operations = {			\
		.write = eeprom_write,									\
		.read = eeprom_read,									\
		.erase = nvs_eeprom_erase								\
	};												\
	static struct nvs_storage_parameters nvs_eeprom_##name##_parameters = {				\
		.write_block_size = 1U,									\
		.erase_value = e_value,									\
		.page_size = s_size									\
	};												\
	static struct nvs_fs nvs_fs_##name = {								\
		.offset = DT_REG_ADDR(DT_NODELABEL(eeprom_partition_label)),				\
		.sector_size = s_size,									\
		.sector_count = s_count,								\
		.storage_device = DEVICE_DT_GET(DT_GPARENT(DT_NODELABEL(eeprom_partition_label))),	\
		.storage_operations = &nvs_eeprom_##name##_operations,					\
		.storage_parameters = &nvs_eeprom_##name##_parameters					\
	};

/**
 * TBD description define for the flash
 *
 * @param eeprom_partition_label partition node label for a eeprom partition
 * @param name name of the nvs structure which is created
 *
 * @return const struct device type pointer
 */
#define NVS_FLASH_DEFINE(flash_partition_label, name) 	\
	static const struct nvs_storage_operations nvs_flash_##name##_operations = {			\
		.write = flash_write,									\
		.read = flash_read,									\
		.erase = flash_erase									\
	};												\
	static struct nvs_storage_parameters nvs_flash_##name##_parameters = {				\
		.write_block_size = 1U,									\
		.erase_value = e_value									\
	};												\
	static struct nvs_fs nvs_fs_##name = {								\
		.offset = FLASH_AREA_OFFSET(flash_partition_label),					\
		.sector_size = s_size,									\
		.sector_count = s_count,								\
		.storage_device = FLASH_AREA_DEVICE(flash_partition_label),				\
		.storage_operations = &nvs_eeprom_operations,						\
		.storage_parameters = &nvs_eeprom_parameters						\
	};

#ifdef __cplusplus
}
#endif

/**
 * @}
 */

#endif /* ZEPHYR_INCLUDE_FS_NVS_H_ */
