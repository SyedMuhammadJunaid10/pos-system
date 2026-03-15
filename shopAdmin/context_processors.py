from django.db import connection

def shop_info(request):
    shop_id = request.session.get("shop_id")

    if not shop_id:
        return {}

    with connection.cursor() as cur:
        cur.execute("SELECT shop_name FROM shops WHERE id=%s", [shop_id])
        shop = cur.fetchone()

    return {
        "shopname": shop[0] if shop else ""
    }