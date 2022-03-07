# script to load environment variables from .env file into bash shell
# run `source load-dotenv.sh`

if [ -f .env ]
then
  export $(cat .env | sed 's/#.*//g' | xargs)
fi
