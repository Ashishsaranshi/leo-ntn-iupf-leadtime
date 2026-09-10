#Run command for sim_figs.py:
python3 sim_figs.py --starlink starlink.txt --iridium iridium.txt --oneweb oneweb.txt

##Expected output
collecting passes ...
  starlink.txt: 106 satellites in the 550+/-25 km / 53+/-2 deg shell
  iridium.txt: 68 satellites in the 780+/-25 km / 86+/-2 deg shell
  oneweb.txt: 645 satellites in the 1200+/-25 km / 87+/-2 deg shell
  propagation window: 2026-09-08 + 7 d (median TLE epoch)
  starlink.txt: 106 satellites in the 550+/-25 km / 53+/-2 deg shell
  iridium.txt: 68 satellites in the 780+/-25 km / 86+/-2 deg shell
  oneweb.txt: 645 satellites in the 1200+/-25 km / 87+/-2 deg shell
Starlink-550: REAL TLEs: starlink.txt
Iridium-780: REAL TLEs: iridium.txt
OneWeb-1200: REAL TLEs: oneweb.txt
Starlink-550: 121 passes, edge RTT ~11.9 ms, lead 68 ms, M 99-244 s
Iridium-780: 118 passes, edge RTT ~15.5 ms, lead 82 ms, M 123-313 s
OneWeb-1200: 143 passes, edge RTT ~20.8 ms, lead 103 ms, M 153-441 s
rep pass: max el 78 deg, dur 8.1 min; grazing M = 99.1 s

=== headline numbers ===
rep 550 pass: culm 78 deg, dur 8.1 min, floor 1-way 1.8 ms, edge 1-way 6.0 ms (RTT 12.0 ms), slant 550-1792 km
  rep pass effective altitude (Eq.1, Re=6371): 540 km
Starlink-550: edge RTT 11.9 ms, lead 66-68 ms, M 99-244 s, worst lead/M 0.07%
Iridium-780: edge RTT 15.5 ms, lead 82-82 ms, M 123-313 s, worst lead/M 0.07%
OneWeb-1200: edge RTT 20.8 ms, lead 103-104 ms, M 153-441 s, worst lead/M 0.07%
grazing 550: M=99.1s  Nmax(mu=100)=9902  batch(5000,500)=10.05s  mg1(5000,500)=0.0499s
overhead 550: Nmax(mu=500) = 122190
overhead 1200: Nmax(mu=500) = 220638

#Run command for fig1.py:
python3 fig1.py

##Expected output
done

