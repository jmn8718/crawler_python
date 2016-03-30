# Load the jinja library's namespace into the current module.
import jinja2
import sys
import json

def to_html_file(filename, content):
	filePath = './output/' +filename +'.html'
	with open( filePath, 'w') as outfile:
		outfile.write(content)

def read_json_file(filename):
	filePath = 'data/' +filename
	json_data = ''
	with open(filePath) as json_file:
		json_data = json.load(json_file)
	return json_data

def template(templateName, templateVars):
	# In this case, we will load templates off the filesystem.
	# This means we must construct a FileSystemLoader object.
	# 
	# The search path can be used to make finding templates by
	#   relative paths much easier.  In this case, we are using
	#   absolute paths and thus set it to the filesystem root.
	templateLoader = jinja2.FileSystemLoader( searchpath="./templates" )

	# An environment provides the data necessary to read and
	#   parse our templates.  We pass in the loader object here.
	templateEnv = jinja2.Environment( loader=templateLoader )

	# This constant string specifies the template file we will use.
	TEMPLATE_FILE = templateName+".jinja"

	# Read the template file using the environment object.
	# This also constructs our Template object.
	template = templateEnv.get_template( TEMPLATE_FILE )

	# Specify any input variables to the template as a dictionary.
	#templateVars = { "title" : "Test Example",
	#                 "description" : "A simple inquiry of function." }

	# Finally, process the template to produce our final text.
	outputText = template.render( templateVars )
	to_html_file(templateName,outputText)
	return outputText

def main(argv):
	dataFileContent = read_json_file(argv[0])
	
	template('index',{ 	"title" : "Crawl Result",
	                 	"result" : [dataFileContent]
		    })

if __name__ == "__main__":
    main(sys.argv[1:])