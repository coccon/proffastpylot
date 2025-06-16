from prfpylot.output.nc_cf_writer import NcWriter

result_path = "results/Sodankyla_SN039_170608-170609/"
writer = NcWriter(result_path)

filename = writer.get_output_filename()
writer.write_nc(filename)
