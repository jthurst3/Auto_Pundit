#!/bin/bash

echo $1
curl -X POST -H "Content-Type: application/json" -d $1 http://localhost:5000/finish_sentence