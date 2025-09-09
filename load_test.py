import socket, ssl
import time
import datetime
import random


INITIAL_RATE = 100  # initial messages per second
INCREASE_RATE = 100  # increase rate every interval
INTERVAL = 300  # seconds to increase the rate
HOST = "localhost"
PORT = 6514


print(f"Connecting to {HOST}:{PORT}...")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
# require a certificate from the server
conn = ctx.wrap_socket(socket.socket(socket.AF_INET),
                           server_hostname=HOST)
conn.connect((HOST, PORT))
print("Done.")


FLOW_IDS = [
    "/Common/sslo_sslo-hsl-test.app/sslo_sslo-hsl-test_accessProfile:Common:a1c76511",
    "/Common/sslo_sslo-hsl-test.app/sslo_sslo-hsl-test_accessProfile:Common:a1c76512",
    "/Common/sslo_sslo-hsl-test.app/sslo_sslo-hsl-test_accessProfile:Common:a1c76513",
    "/Common/sslo_sslo-hsl-test.app/sslo_sslo-hsl-test_accessProfile:Common:a1c76514",
    "/Common/sslo_sslo-hsl-test.app/sslo_sslo-hsl-test_accessProfile:Common:a1c76515",
    "/Common/blah-blah.app/blah-blah_accessProfile:Common:a1c76511",
    "/Common/blah-blah.app/blah-blah_accessProfile:Common:a1c76512",
    "/Common/blah-blah.app/blah-blah_accessProfile:Common:a1c76513",
    "/Common/blah-blah.app/blah-blah_accessProfile:Common:a1c76514",
    "/Common/blah-blah.app/blah-blah_accessProfile:Common:a1c76515",
    "/Common/foo.app/foo_accessProfile:Common:a1c76511",
    "/Common/foo.app/foo_accessProfile:Common:a1c76512",
    "/Common/foo.app/foo_accessProfile:Common:a1c76513",
    "/Common/foo.app/foo_accessProfile:Common:a1c76514",
    "/Common/foo.app/foo_accessProfile:Common:a1c76515"
]


DST_IPS = [
    "192.168.1.1:443",
    "192.168.1.2:443",
    "192.168.1.3:443",
    "192.168.1.4:443",
    "192.168.1.5:443",
    "192.168.100.101:22",
    "192.168.100.102:22",
    "192.168.100.103:22",
    "192.168.100.104:22",
    "192.168.100.105:22",
    "192.168.200.201:443",
    "192.168.200.202:443",
    "192.168.200.203:443",
    "192.168.200.204:443",
    "192.168.200.205:443",
]

SSL_CHOICES = [
    "TLSv1.3 ECDHE-RSA-AES128-GCM-SHA256",
    "TLSv1.1 ECDHE-RSA-AES128-GCM-SHA256",
    "TLSv1.2 ECDHE-RSA-AES256-GCM-SHA384",
    "TLSv1.1 ECDHE-RSA-AES128-GCM-SHA256",
    "TLSv1.2 ECDHE-RSA-AES256-GCM-SHA384",
    "TLSv1.1 ECDHE-RSA-AES128-GCM-SHA256",
    "TLSv1.1 ECDHE-RSA-AES128-GCM-SHA256",
    "TLSv1.2 ECDHE-RSA-AES256-GCM-SHA384",
    "TLSv1.1 ECDHE-RSA-AES128-GCM-SHA256",
    "TLSv1.2 ECDHE-RSA-AES256-GCM-SHA384",
    "TLSv1.2 ECDHE-ECDSA-AES256-SHA384",
    "TLSv1.2 ECDHE-ECDSA-AES256-SHA384",
    "TLSv1.3 ECDHE-ECDSA-AES256-SHA384",
    "TLSv1.3 ECDHE-ECDSA-AES256-SHA384",
    "TLSv1.3 ECDHE-ECDSA-AES256-SHA384",
]

def get_data_to_send():
    hostnames = [x for x in [
            "sslo-hsl-test.example.com",
            "blah.example.com",
            "foo.app"
        ] for _ in range(5)]

    vips = [x for x in [
            "/Common/sslo_sslo-hsl-test.app/sslo_sslo-hsl-test-in-t-4",
            "/Common/blah-blah.app/blah-blah-in-t-4",
            "/Common/foo.app/foo-in-t-4"
        ] for _ in range(5)]
    l7_choices = [x for x in ["https", "ssh", "https"] for _ in range(5)]
    decrypted_choices = [x for x in ["decrypted", "bypassed", "unencrypted"] for _ in range(5)]
    service_paths = [x for x in ["ssloSC_all_services", "ssloSC_some_services", "ssloSC_no_services"] for _ in range(5)]
    reset_causes = [x for x in ["NA","solar-flare","coffe_spilled_on_session"] for _ in range(5)]
    policy_choices = [x for x in ["All Traffic", "Some Traffic", "Most Traffic"] for _ in range(5)]
    url_choices = [x for x in ["/Common/Information_Technology", "/Common/Another_One", "/Common/Something"] for _ in range(5)]
    ingress_choices = [x for x in ["_loopback", "ifEth1.1", "ifEth2.1"] for _ in range(5)]
    egress_choices = [x for x in ["/Common/outbound-vlan", "/Common/outbound-vlan2", "/Common/outbound-vlan3"] for _ in range(5)]

    # tcp 10.1.10.50:52336 -> 93.184.215.14:443 clientSSL: TLSv1.2 ECDHE-RSA-AES128-GCM-SHA256 serverSSL: TLSv1.2 ECDHE-RSA-AES128-GCM-SHA256 L7 https (www.example.com) decryption-status: decrypted duration: 57 msec service-path: ssloSC_all_services client-bytes-in: 1358 client-bytes-out: 4717 server-bytes-in: 5691 server-bytes-out: 962 client-tls-handshake: completed server-tls-handshake: completed reset-cause: 'NA' policy-rule: 'All Traffic' url-category: /Common/Information_Technology ingress: _loopback egress: /Common/outbound-vlan

    numbers = list(range(15))
    weights = [i+1 for i in range(15)]
    ret_data = []
    for _ in range(10000):
        rand_idx = random.choices(numbers, weights=weights, k=1)[0]  
        ret_data.append("%s %s Traffic summary - %s %s -> %s clientSSL: %s serverSSL: %s L7 %s (%s) decryption-status: %s duration: %d msec service-path: %s client-bytes-in: %d client-bytes-out: %d server-bytes-in: %d server-bytes-out: %d client-tls-handshake: %s server-tls-handshake: %s reset-cause: '%s' policy-rule: '%s' url-category: %s ingress: %s egress: %s\n" % (
            FLOW_IDS[rand_idx],
            vips[rand_idx],
            random.choice(["tcp", "udp"]),
            f"10.1.{random.randint(0,255)}.{random.randint(0,255)}:{random.randint(49152,65535)}",
            DST_IPS[rand_idx],
            SSL_CHOICES[rand_idx],
            SSL_CHOICES[rand_idx],
            l7_choices[rand_idx],
            hostnames[rand_idx],
            decrypted_choices[rand_idx],
            random.randint(1, 500),
            service_paths[rand_idx],
            random.randint(500, 5000),
            random.randint(1000, 10000),
            random.randint(500, 5000),
            random.randint(1000, 10000),
            random.choice(["completed", "not-completed", "some-other-status"]),
            random.choice(["completed", "not-completed", "some-other-status"]),
            reset_causes[rand_idx],
            policy_choices[rand_idx],
            url_choices[rand_idx],
            ingress_choices[rand_idx],
            egress_choices[rand_idx]
        ))
    return ret_data


try:
    count = 0
    start  = time.time()
    send_data = get_data_to_send()
    current_rate = INITIAL_RATE
    next_increase_time = start + INTERVAL
    batch_count = 0
    nowish = f"{datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','')}Z"
    while True:
        for data in send_data:
            count +=1
            batch_count += 1
            send = str.encode(f"<118>1 {nowish} 17-1-demo.f5kc.com F5-API-Discovery - - - {data}")
            conn.send(send)
            if count % 100000 == 0 or batch_count >= current_rate:
                nowish = f"{datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','')}Z"
                if batch_count >= current_rate:
                    time.sleep(1)
                batch_count = 0
                now = time.time()
                rate = count / (now-start)
                print(f'Now: {now} Sent: {count} messages ({rate} msg/sec)')
                send_data = get_data_to_send()
                if now >= next_increase_time:
                    start  = time.time()
                    count = 0
                    if current_rate < 10000:
                        current_rate = current_rate * INCREASE_RATE
                    else:
                        current_rate += 5000
                    next_increase_time = now + INTERVAL
                    print(f'Increased rate to: {current_rate} msg/sec')
                break
except KeyboardInterrupt:
    print("Interrupted by user. Shutting down...")
finally:
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()
