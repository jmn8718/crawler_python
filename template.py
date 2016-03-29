# Load the jinja library's namespace into the current module.
import jinja2

def to_html_file(filename, content):
	filePath = './output/' +filename +'.html'
	with open( filePath, 'w') as outfile:
		outfile.write(content)

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

def main():
	template('index',{ 	"title" : "Crawl Result",
	                 	"result" : [{
						  	"http://www.bbvaapimarket.com/": [
							    "https://www.bbvaapimarket.com/web/api_market/cookies-policy", 
							    "https://www.bbvaapimarket.com/web/api_market/home?p_p_auth=E1Z5mFGD&p_p_id=49&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&_49_struts_action=%2Fmy_sites%2Fview&_49_groupId=12308&_49_privateLayout=false", 
							    "https://www.bbvaapimarket.com/web/api_market/home", 
							    "https://www.bbvaapimarket.com/c/portal/login?p_l_id=12313"
							    ]
					    },{
					    	"https://www.bbvaapimarket.com/web/api_market/cookies-policy": [
							    "NotFound"
							    ]
					    }]
		    })

if __name__ == "__main__":
    main()