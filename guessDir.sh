docker run --rm -v $1:/tf_files -v $2:/toScan -v $3:/scanned xblaster/tensor-guess sh -c "python py/label_dir.py"
#docker run --rm -it  -v $1:/tf_files -v $2:/toScan -v $3:/scanned tf bash
