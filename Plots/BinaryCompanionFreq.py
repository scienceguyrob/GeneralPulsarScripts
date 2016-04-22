import numpy as np
import matplotlib.pyplot as plt

alphab = ["Unknown","CO or ONeMg White Dwarf","CO or ONeMg White Dwarf?",
          "Helium White Dwarf","Helium White Dwarf?","Helium White Dwarf (T)",
          "Main-sequence star","Main-sequence star?",
          "Neutron star","Neutron star?",
          "Ultra-light companion","Ultra-light companion?","Ultra-light companion (T)"]

alphab = ["?","CO WD","CO WD?",
          "He WD","He WD?","He WD (T)",
          "MS Star","MS Star?",
          "NS","NS?",
          "UL","UL?","UL (T)"]

frequencies = [35,30,5,106,7,2,14,3,11,2,40,1,1]

# Ordered.
frequencies = [106,40,35,30,14,11,7,5,3,2,2,1,1]

alphab = ["He WD","UL","?","CO WD","MS Star","NS","He WD?",
          "CO WD?","MS Star?","He WD (T)","NS?","UL (T)","UL?"]

pos = np.arange(len(alphab))
width = 1.0     # gives histogram aspect to the bar diagram

ax = plt.axes()
ax.set_xticks(pos + (width / 2))
ax.set_xticklabels(alphab)

plt.bar(pos, frequencies, width, color='r')
plt.title("Histogram of Binary Companions")
plt.xlabel("Companion type")
plt.ylabel("Frequency")
plt.show()