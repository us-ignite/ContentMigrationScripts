from djangosite.wp_data_importer import run_imports

if __name__ == "__main__":
    import os
    os.chdir(os.getcwd())

    run_imports()