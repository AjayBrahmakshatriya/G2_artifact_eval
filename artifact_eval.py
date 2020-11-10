import os
import subprocess
DIR_PATH=os.path.dirname(os.path.realpath(__file__)).rstrip("/")

SCRATCH_PATH=""
GRAPHIT_BUILD_PATH=""
DATASET_PATH=""
APPS_DIRECTORY=""
GPU_ID=""
NVCC_PATH=""
CXX_COMPILER=""
NVCC_COMMAND=""
GPU_PREFIX=""


ORKUT=""
TWITTER=""
LIVEJOURNAL=""
SINAWEIBO=""
HOLLYWOOD=""
INDOCHINA=""
RUSA=""
RCA=""
RCENTRAL=""
GRAPH_ALL=[]
GRAPH_SOCIAL=[]
GRAPH_ROAD=[]

def find_dataset_files():
	global ORKUT
	global TWITTER
	global LIVEJOURNAL
	global SINAWEIBO
	global HOLLYWOOD
	global INDOCHINA
	global RUSA
	global RCA
	global RCENTRAL
	global GRAPH_ALL
	global GRAPH_ROAD
	global GRAPH_SOCIAL

	ORKUT=DATASET_PATH+"/soc-orkut.mtx"
	TWITTER=DATASET_PATH+"/soc-twitter-2010.mtx"
	LIVEJOURNAL=DATASET_PATH+"/soc-LiveJournal1.mtx"
	SINAWEIBO=DATASET_PATH+"/soc-sinaweibo.mtx"
	HOLLYWOOD=DATASET_PATH+"/hollywood-2009.weighted.mtx"
	INDOCHINA=DATASET_PATH+"/indochina-2004.weighted.mtx"
	RUSA=DATASET_PATH+"/road_usa.weighted.mtx"
	RCA=DATASET_PATH+"/roadNet-CA.weighted.mtx"
	RCENTRAL=DATASET_PATH+"/road_central.weighted.mtx"
	
	GRAPH_SOCIAL=[('orkut', ORKUT), ('twitter', TWITTER), ('livejournal', LIVEJOURNAL), ('sinaweibo', SINAWEIBO), ('indochina', INDOCHINA), ('hollywood', HOLLYWOOD)]
	GRAPH_ROAD=[('rca', RCA), ('rusa', RUSA), ('rcentral', RCENTRAL)]
	GRAPH_ALL = GRAPH_SOCIAL + GRAPH_ROAD

	

def read_default_path(message, default):
	print(message + " [" + default + "]: ", end="")
	val = input().strip().rstrip("/")
	if val == "":
		val = default	
	return val

def get_gpu_count():
	gpus = os.popen("nvidia-smi -L").read().strip()
	return len(gpus.split("\n"))

def get_command_output(command):
	output = ""
	if isinstance(command, list):
		proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	else:
		proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	exitcode = proc.wait()
	if exitcode != 0:
		print(command)
	assert(exitcode == 0)
	for line in proc.stdout.readlines():
		if isinstance(line, bytes):
			line = line.decode()
		output += line.rstrip() + "\n"
	proc.stdout.close()
	return output

def set_NVCC_COMMAND(CTA_STYLE=-1, MAX_REG=-1):
	global NVCC_COMMAND
	
	NVCC_COMMAND = NVCC_PATH + " -ccbin " + CXX_COMPILER + " "
	
	get_command_output(NVCC_COMMAND + APPS_DIRECTORY + "/obtain_gpu_cc.cu -o obtain_gpu_cc")
	output = get_command_output(GPU_PREFIX+"./obtain_gpu_cc").split()

	if len(output) != 2:
		print ("Cannot obtain GPU information")
		exit(-1)
	compute_capability = output[0]
	num_of_sm = output[1]

	if CTA_STYLE == -1:
		NVCC_COMMAND += " -rdc=true -DNUM_CTA=" + str(int(num_of_sm)*2) + " -DCTA_SIZE=512 -gencode arch=compute_" + compute_capability + ",code=sm_" + compute_capability
	else:
		NVCC_COMMAND += " -rdc=true -DNUM_CTA=" + str(CTA_STYLE[0]) + " -DCTA_SIZE=" + str(CTA_STYLE[1]) + " -gencode arch=compute_" + compute_capability + ",code=sm_" + compute_capability

	if MAX_REG == -1:
		NVCC_COMMAND += " -std=c++11 -O3 -I " + DIR_PATH+"/graphit" + "/src/runtime_lib/ -Xcompiler \"-w\" -Wno-deprecated-gpu-targets --use_fast_math -Xptxas \" -dlcm=ca --maxrregcount=64\" "
	else:
		NVCC_COMMAND += " -std=c++11 -O3 -I " + DIR_PATH+"/graphit" + "/src/runtime_lib/ -Xcompiler \"-w\" -Wno-deprecated-gpu-targets --use_fast_math -Xptxas \" -dlcm=ca --maxrregcount=" + str(MAX_REG) + "\" "
	# print(NVCC_COMMAND)


def compile_application(gtfile, binname):
	if os.path.exists(binname):
		return
	get_command_output("python3 " + GRAPHIT_BUILD_PATH + "/bin/graphitc.py -f " + APPS_DIRECTORY + "/" + gtfile + " -o " + gtfile + ".cu")
	get_command_output(NVCC_COMMAND + gtfile + ".cu -o " + binname)


def run_sanity_check():
	compile_application("simple_graph_load.gt", "load")
	print(get_command_output(GPU_PREFIX+"./load " + RCA))


def compile_and_run(gtfile, binname, run_args, outputf):
	compile_application(gtfile, binname)
	output = get_command_output(GPU_PREFIX+"./"+binname + " " + run_args)
	f = open(outputf, "w")
	f.write(output)
	f.close()


def run_pr():
	set_NVCC_COMMAND()
	print("Running eval for Pagerank")
	PR = "pr.gt"	
	for i, (name, graph) in enumerate(GRAPH_ALL):
		compile_and_run(PR, "pr", graph, "pr_" + name + ".out")
		print(str(i+1) + "/" + str(len(GRAPH_ALL)))


def run_cc():
	set_NVCC_COMMAND()
	print("Running eval for Connected Components")
	CC = "cc.gt"	
	for i, (name, graph) in enumerate(GRAPH_ALL):
		compile_and_run(CC, "cc", graph, "cc_" + name + ".out")
		print(str(i+1) + "/" + str(len(GRAPH_ALL)))


def run_ds():
	delta = {}
	delta["orkut"] = 22
	delta["livejournal"] = 120
	delta["twitter"] = 15
	delta["sinaweibo"] = 15
	delta["hollywood"] = 15
	delta["indochina"] = 20
	delta["rusa"] = 80000
	delta["rcentral"] = 30000
	delta["rca"] = 20000
	
	print ("Running eval for Delta Stepping")
	DS_SOCIAL = "ds_social.gt"
	DS_ROAD = "ds_road.gt"
	set_NVCC_COMMAND()
	for i, (name, graph) in enumerate(GRAPH_SOCIAL):
		compile_and_run(DS_SOCIAL, "ds_social", graph + " 0 " + str(delta[name]), "ds_" + name + ".out")
		print(str(i+1) + "/" + str(len(GRAPH_ALL)))
	set_NVCC_COMMAND((40, 256), 512)
	for i, (name, graph) in enumerate(GRAPH_ROAD):
		compile_and_run(DS_ROAD, "ds_road", graph + " 0 " + str(delta[name]), "ds_" + name + ".out")
		print(str(i+1+len(GRAPH_SOCIAL)) + "/" + str(len(GRAPH_ALL)))
		
	

def run_tests():
	# get the GPU properties first
	set_NVCC_COMMAND()
	find_dataset_files()
	run_sanity_check()
	# run_pr()
	# run_cc()
	run_ds()
	
	
def main():
	global SCRATCH_PATH
	global GRAPHIT_BUILD_PATH
	global DATASET_PATH
	global APPS_DIRECTORY
	global GPU_ID
	global NVCC_PATH
	global CXX_COMPILER
	global GPU_PREFIX

	print("Starting artifact evaluation in directory: ", DIR_PATH)
	SCRATCH_PATH = read_default_path("Please choose a scratch directory to use", DIR_PATH + "/scratch")
	GRAPHIT_BUILD_PATH = read_default_path("Please choose GraphIt build directory", DIR_PATH + "/graphit/build")
	DATASET_PATH = read_default_path("Please choose dataset path", DIR_PATH + "/dataset")
	APPS_DIRECTORY = DIR_PATH+"/apps"
	NVCC_PATH = read_default_path("Please choose NVCC path", "/usr/local/cuda/bin/nvcc")
	CXX_COMPILER = read_default_path("Please choose CXX_COMPILER", "/usr/bin/g++")
	
	if os.path.exists(SCRATCH_PATH):
		os.system("rm -rf " + SCRATCH_PATH)
	os.makedirs(SCRATCH_PATH)
	
	os.chdir(SCRATCH_PATH)


	total_devices = get_gpu_count()
	GPU_ID = read_default_path("Choose GPU id to use (0-" + str(total_devices-1) + ")", str(0))
	GPU_PREFIX="CUDA_VISIBLE_DEVICES="+GPU_ID+" "
	
	# print(SCRATCH_PATH, GRAPHIT_BUILD_PATH, DATASET_PATH, GPU_ID, NVCC_PATH)

	run_tests()






if __name__ == "__main__":
	main()
