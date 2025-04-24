For splitting into 60:20:20
Folder format (e.g. C:/Users/username/Download/FireNet/Combined) (where it contains 0000.jpg, 0000.xml, 0001.jpg etc.)

first run for_overview_in_system_folder
then run for_classes
then run for_sort_duplicates (keeping dups img into biggest classes only, and split into 60:20:20 for train:validate:test)
then run for_folder_sort_classes
then run for_folder_sort_use
then run for_filter_out_no_used_class
then run for_sorting_finial_big_3_folders
