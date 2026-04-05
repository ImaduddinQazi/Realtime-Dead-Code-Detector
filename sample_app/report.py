from analyzer import analyze_routes, analyze_tables

def print_report():
    print("\n" + "="*60)
    print("  DEAD CODE DETECTOR — ROUTE ANALYSIS")
    print("="*60)

    routes = analyze_routes()
    for r in routes:
        icon = "🔴" if r["status"] == "DEAD" else "🟡" if r["status"] == "WARN" else "🟢"
        print(f"\n{icon}  {r['method']} {r['path']}")
        print(f"   Status      : {r['status']}")
        print(f"   Total calls : {r['total_calls']}")
        print(f"   Last seen   : {r['last_seen']}")
        print(f"   Confidence  : {r['confidence']}% likely dead")

    print("\n" + "="*60)
    print("  TABLE ANALYSIS")
    print("="*60)

    tables = analyze_tables()
    for t in tables:
        icon = "🔴" if t["status"] == "DEAD" else "🟡" if t["status"] == "WARN" else "🟢"
        print(f"\n{icon}  {t['table']}")
        print(f"   Status      : {t['status']}")
        print(f"   Total hits  : {t['total_hits']}")
        print(f"   Last seen   : {t['last_seen']}")
        print(f"   Confidence  : {t['confidence']}% likely dead")

    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    print_report()