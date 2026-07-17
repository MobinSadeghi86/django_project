import json
import secrets
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime, timedelta
from .m import User, Villa, Availability, Reservation,Payment, Token
def tk(q):
    a = q.META.get('HTTP_AUTHORIZATION')
    if not a:
        return None
    try:
        k = a.split()[1]
        t = Token.objects.get(key=k)
        return t.user_id
    except:
        return None
@csrf_exempt
def rg(q):
    if q.method == 'POST':
        d = json.loads(q.body)
        p = make_password(d['password'])
        u = User.objects.create(full_name=d['full_name'], email=d['email'], role=d['role'], password=p)
        return JsonResponse({'id': u.user_id, 'status': 'ok'})
@csrf_exempt
def lg(q):
    if q.method == 'POST':
        d = json.loads(q.body)
        try:
            u = User.objects.get(email=d['email'])
            if check_password(d['password'], u.password):
                k = secrets.token_hex(20)
                t = Token.objects.create(user_id=u, key=k)
                return JsonResponse({'token': k, 'id': u.user_id, 'role': u.role, 'status': 'ok'})
            return JsonResponse({'status': 'failed'}, status=401)
        except:
            return JsonResponse({'status': 'failed'}, status=401)
@csrf_exempt
def cv(q):
    if q.method == 'POST':
        u = tk(q)
        if not u or u.role != 'host':
            return JsonResponse({'status': 'unauthorized'}, status=401)
        d = json.loads(q.body)
        v = Villa.objects.create(host_id=u, title=d['title'], city=d['city'], address=d['address'], price_per_night=d['price_per_night'], capacity=d['capacity'], amenities=d['amenities'])
        if 'dates' in d:
            for s in d['dates']:
                t = datetime.strptime(s, '%Y-%m-%d').date()
                Availability.objects.create(villa_id=v, date=t, is_available=True)
        return JsonResponse({'id': v.villa_id, 'status': 'ok'})
def sv(q):
    c = q.GET.get('city')
    i = q.GET.get('check_in')
    o = q.GET.get('check_out')
    v = Villa.objects.filter(city=c)
    if i and o:
        t1 = datetime.strptime(i, '%Y-%m-%d').date()
        t2 = datetime.strptime(o, '%Y-%m-%d').date()
        g = []
        cu = t1
        while cu < t2:
            g.append(cu)
            cu += timedelta(1)
        n = len(g)
        r = []
        for x in v:
            cn = Availability.objects.filter(villa_id=x, date__in=g, is_available=True).count()
            if cn == n:
                r.append({'id': x.villa_id, 'title': x.title, 'price_per_night': x.price_per_night})
        return JsonResponse(r, safe=False)
    r = [{'id': x.villa_id, 'title': x.title, 'price_per_night': x.price_per_night} for x in v]
    return JsonResponse(r, safe=False)
def dv(q,  pk):
    try:
        x = Villa.objects.get(villa_id=pk)
        a = Availability.objects.filter(villa_id=x, is_available=True)
        d = [str(y.date) for y in a]
        return JsonResponse({'id': x.villa_id, 'title': x.title, 'city': x.city, 'address': x.address, 'price_per_night': x.price_per_night, 'capacity': x.capacity, 'amenities': x.amenities, 'availability': d})
    except:
        return JsonResponse({'status': 'not found'}, status=404)
@csrf_exempt
def br(q):
    if q.method == 'POST':
        u = tk(q)
        if not u or u.role != 'guest':
            return   JsonResponse({'status': 'unauthorized'}, status=401)
        d = json.loads(q.body)
        v = d['villa_id']
        t1 = datetime.strptime(d['check_in'], '%Y-%m-%d').date()
        t2 = datetime.strptime(d['check_out'], '%Y-%m-%d').date()
        try:
            with transaction.atomic():
                m = Villa.objects.get(villa_id=v)
                dy = []
                cu = t1
                while cu < t2:
                    dy.append(cu)
                    cu += timedelta(1)
                n = len(dy)
                al = Availability.objects.select_for_update().filter(villa_id=m, date__in=dy, is_available=True)
                if len(al) != n:
                    return JsonResponse({'status': 'failed'}, status=400)
                for a in al:
                    a.is_available = False
                    a.save()
                p = m.price_per_night * n
                r = Reservation.objects.create(guest_id=u, villa_id=m, check_in=t1, check_out=t2, total_price=p, status='pending_payment')
                k = Payment.objects.create(reservation_id=r, amount=p, status='pending')
                return JsonResponse({'reservation_id': r.reservation_id, 'status': r.status, 'total_price': r.total_price})
        except:
            return JsonResponse({'status': 'error'}, status=500)
@csrf_exempt
def vp(q):
    if q.method == 'POST':
        d = json.loads(q.body)
        p = Payment.objects.get(payment_id=d['payment_id'])
        r = p.reservation_id
        if d['status'] == 'success':
            p.status='success'
            p.gateway_ref = d.get('gateway_ref', '')
            p.save()
            r.status='confirmed'
            r.save()
            return JsonResponse({'status': 'confirmed'})
        else:
            p.status='failed'
            p.save()
            r.status = 'failed'
            r.save()
            dy = []
            cu = r.check_in
            while cu < r.check_out:
                dy.append(cu)
                cu += timedelta(1)
            Availability.objects.filter(villa_id=r.villa_id, date__in=dy).update(is_available=True)
            return JsonResponse({'status': 'failed'})
def hr(q):
    u = tk(q)
    if not u:
        return JsonResponse({'status': 'unauthorized'}, status=401)
    s = Reservation.objects.filter(guest_id=u)
    r = [{'id': x.reservation_id, 'villa_id': x.villa_id_id, 'check_in': str(x.check_in), 'check_out': str(x.check_out), 'total_price': x.total_price, 'status': x.status} for x in s]
    return JsonResponse(r, safe=False)