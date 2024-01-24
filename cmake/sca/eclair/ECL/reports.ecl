# eclair_report

# This file must not be renamed: it is referenced by eclair-make.sh
#
# The aim of this file is to define the eclair_report configuration
# common to IDE analyses.

quiet()

# NEEDED: set the variable for the binary output directory from the environment
# variable.
setq(data_dir,getenv("ECLAIR_DATA_DIR"))

# NEEDED: set the variable for the ECLAIR project database from the environment
# variable.
setq(ecd_file,getenv("ECLAIR_PROJECT_ECD"))

# NEEDED: set the variable for the output directory from the environment
# variable.
setq(output_dir,getenv("ECLAIR_OUTPUT_DIR"))

if(file_exists(ecd_file),
   db(ecd_file),
 create_db(ecd_file))

server_root("")
server("changing")

setq(loaded_dir,join_paths(data_dir,"loaded"))
make_dirs(loaded_dir)

# NEEDED: generate the ecd from frame files
strings_map("load_ecb",500,"",".+\\.ecb",0,setq(ecb,join_paths(data_dir,$0)),load(ecb),rename(ecb,join_paths(loaded_dir,$0)))
strings_map("load_ecb",500,"",".*",0)

loading()
map_strings("load_ecb", dir_entries(data_dir))
loaded()

if(string_equal(or(getenv("ECLAIR_metrics_tab"),"false"),"true")
   metrics_tab(join_paths(output_dir,"metrics")))

if(string_equal(or(getenv("ECLAIR_reports_tab"),"false"),"true")
   reports_tab(join_paths(output_dir,"reports")))

if(string_equal(or(getenv("ECLAIR_summary_txt"),"false"),"true")
   summary_txt(join_paths(output_dir,"summary_txt")))

if(string_equal(or(getenv("ECLAIR_summary_doc"),"false"),"true")
   summary_doc(join_paths(output_dir,"summary_doc")))

if(string_equal(or(getenv("ECLAIR_summary_odt"),"false"),"true")
   summary_odt(join_paths(output_dir,"summary_odt")))

if(string_equal(or(getenv("ECLAIR_full_txt_areas"),"true"),"true")
   setq(report_areas,"areas"),
   setq(report_areas,"first_area"))
if(string_equal(or(getenv("ECLAIR_full_txt"),"false"),"true")
   full_txt(join_paths(output_dir,"txt")))

if(string_equal(or(getenv("ECLAIR_full_doc_areas"),"false"),"true")
   setq(report_areas,"areas"),
   setq(report_areas,"first_area"))
if(string_equal(or(getenv("ECLAIR_full_doc"),"false"),"true")
   full_doc(join_paths(output_dir,"doc")))
if(string_equal(or(getenv("ECLAIR_full_odt"),"false"),"true")
   full_odt(join_paths(output_dir,"odt")))

server("changed")
