# Login

`ibmcloud login`

# Set Region

`ibmcloud target -r LOC`

# Get Region

`ibmcloud account orgs -r all`

# Deploy 
`zip -r functionName.zip *.py virtualenv requirements.txt`
`ibmcloud fn action update CLOUDFUNCTIONNAME --kind python:3.7 functionName.zip`
