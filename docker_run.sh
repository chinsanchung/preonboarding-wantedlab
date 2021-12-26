#!/bin/bash
app='preonboarding-wantedlab'

docker build -t ${app} .

docker run -d -p 8080:5000 --name ${app} ${app}
