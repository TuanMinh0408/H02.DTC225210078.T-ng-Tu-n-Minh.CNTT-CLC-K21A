def main():
    with open('tuan_all_text.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("TOTAL LINES IN DUMPED TEXT:", len(lines))
    
    keywords = ['an ninh', 'vai trò', 'té ngã', 'bác sĩ', 'shipper', 'cam đoan']
    counts = {kw: 0 for kw in keywords}
    
    for line in lines:
        for kw in keywords:
            if kw in line.lower():
                counts[kw] += 1
                
    for kw, cnt in counts.items():
        print(f"Keyword '{kw}': {cnt} times")

if __name__ == '__main__':
    main()
