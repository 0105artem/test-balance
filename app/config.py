from environs import Env

env = Env()
env.read_env()


class Config:
    DEBUG = env.bool("DEBUG", default=False)
    HOST = env.str("HOST")
    PORT = env.str("PORT")
    DATABASE_URI = env.str("DATABASE_URI")
