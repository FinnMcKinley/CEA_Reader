import re
import matplotlib.pyplot as plt

# Initialize data storage
data = {}

# Define patterns for pressure, O/F ratio, and Isp values
pressure_pattern = re.compile(r'\s*P,\s*BAR\s+(\d+\.\d+)')
of_pattern = re.compile(r'\s*O/F=\s*(\d+\.\d+)')
isp_pattern = re.compile(r'Isp, M/SEC\s+([\d.\s]+)')

# User choice: Select 'first', 'last', or 'both' Isp values for plotting
userStupid = True
while userStupid:
    isp_choice = input("Do you want to use the 'first', 'last', or 'both' Isp values? ").strip().lower()
    if isp_choice in ['first', 'last', 'both']:
        userStupid = False
    else:
        print("Invalid choice! Please enter 'first', 'last', or 'both'.")

fileNotFound = True
while fileNotFound:
    filepath = input("What is the name of the CEA file?")
    try:
        testfile = open(filepath, 'r')
        line1 = testfile.readline()
        testfile.close()
    except FileNotFoundError:
        print("FileNotFoundError: Please try a different file/path!")
    except FileExistsError:
        print("FileExistsError: Please try a different file/path!")
    except OSError:
        print("OSError: Try something else ¯\_(ツ)_/¯")
    except:
        print("Try something else ¯\_(ツ)_/¯")
    else:
        fileNotFound = False

# Open the text file and read the content
with open(filepath, 'r') as file:
    lines = file.readlines()
    current_pressure = None
    pending_of = None  # Temporary storage to ensure the first O/F isn't missed

    for line in lines:
        # Detect and store chamber pressure
        pressure_match = pressure_pattern.search(line)
        if pressure_match:
            current_pressure = float(pressure_match.group(1))
            if current_pressure not in data:
                data[current_pressure] = {'o_f': [], 'isp': []}

            # If a pending O/F exists, store it with the current pressure
            if pending_of is not None:
                data[current_pressure]['o_f'].append(pending_of)
                pending_of = None  # Reset pending O/F

        # Detect and temporarily store the O/F ratio
        of_match = of_pattern.search(line)
        if of_match:
            pending_of = float(of_match.group(1))  # Save for the next matching pressure

        # Detect and store Isp values (first and last)
        isp_match = isp_pattern.search(line)
        if isp_match and current_pressure is not None:
            isp_values = list(map(float, isp_match.group(1).split()))
            if isp_values:
                # Store both the first and last Isp values
                data[current_pressure]['isp'].append((isp_values[0], isp_values[-1]))

# Debugging: Print extracted data to verify
# print("\nExtracted Data:")
# for pressure, values in data.items():
#     print(f"Pressure: {pressure} bar, O/F: {values['o_f']}, Isp: {values['isp']}")

# Plotting the data based on the user's choice
plt.figure(figsize=(10, 6))

for pressure, values in data.items():
    if len(values['o_f']) == len(values['isp']):
        o_f = values['o_f']

        if isp_choice in ['first', 'both']:
            isp_first = [isp[0] for isp in values['isp']]  # Use first Isp value
            plt.plot(o_f, isp_first, label=f'{pressure} bar - Throat Isp', linestyle='dashed')

        if isp_choice in ['last', 'both']:
            isp_last = [isp[1] for isp in values['isp']]  # Use last Isp value
            plt.plot(o_f, isp_last, label=f'{pressure} bar - Nozzle Isp')

plt.xlabel('O/F Ratio')
plt.ylabel('Specific Impulse (m/s)')
plt.title(f'Specific Impulse vs O/F Ratio ({isp_choice.capitalize()} Isp Values)')
plt.legend()
plt.grid(True)
plt.show()

# Function to find the best O/F ratio for the highest Isp
best_of_ratios = {}

for pressure, values in data.items():
    if len(values['o_f']) == len(values['isp']):
        best_isp = -1  # Start with a low value
        best_of = None
        
        for o_f, isp in zip(values['o_f'], values['isp']):
            max_isp = max(isp)  # Get the highest Isp (either first or last value)
            if max_isp > best_isp:
                best_isp = max_isp
                best_of = o_f
        
        best_of_ratios[pressure] = (best_of, best_isp)

# Print results
print("Best O/F Ratios for Highest Isp:")
for pressure, (best_of, best_isp) in best_of_ratios.items():
    print(f"Pressure: {pressure} bar -> Best O/F: {best_of}, Max Isp: {best_isp} m/s")