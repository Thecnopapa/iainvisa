
testing (){
    if [[ "$*" == *"tunnel"* ]]; then
        export START_NGROK=1
    else
        export START_NGROK=0
    fi

    if [[ "$*" == *"--no-secrets"* ]]; then
        export FETCH_SECRETS=0
    else
        export FETCH_SECRETS=1
    fi

    if [[ "$*" == *"debug"* ]]; then
        flask --app main run --host="0.0.0.0" --port=5000 --debug
    else
        flask --app main run --host="0.0.0.0" --port=5000
    fi


}
deploy (){
    gcloud config set project iainvisa
	cd $PROJECT_PATH && gcloud run deploy --source .
}
latest () {
    gcloud config set project iainvisa
    cd $PROJECT_PATH && gcloud run services update-traffic --to-latest
}

