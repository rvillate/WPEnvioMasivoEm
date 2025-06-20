import datetime

def log_print(mensaje, error=False, es_inicio=None, mostrar=True):
    if not mostrar:
        return

    now = datetime.datetime.now()
    error_msg = ""
    es_inicio_msg = ""

    if error:
        error_msg = "Error: "

    if es_inicio is True and not error:
        es_inicio_msg = ": INICIO"
    elif es_inicio is False and not error:
        es_inicio_msg = ": FIN"

    print(f"{now.strftime('%Y-%m-%d %H:%M:%S')} {error_msg}{mensaje}{es_inicio_msg}")