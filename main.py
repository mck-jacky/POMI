# main file
import psycopg2
import sys

db = None

def main():
    try:
        db = psycopg2.connect(dbname="COMP3900")
        runprogram()
    except psycopg2.Error as err:
        print("DB error: ", err)
    except Exception as err:
        print("Internal Error: ", err)
        raise err
    finally:
        if db is not None:
            db.close()
    sys.exit(0)


def runprogram():
    pass


if __name__ == "__main__":
    main()