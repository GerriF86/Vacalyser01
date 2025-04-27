import streamlit as st
from src.utils.ui import apply_base_styling
import matplotlib.pyplot as plt
import math

st.set_page_config(page_title="ROI & Profit - Vacalyser", layout="wide")
apply_base_styling()

st.title("Efficiency, Quality & Profit")
st.write("""
Vacalyser is designed to optimize the recruitment **time, quality, and cost** – the three corners of the hiring triangle.
By balancing these factors, organizations can significantly improve their ROI on hiring.
""")
st.write("Below is the **Candidate Experience Triangle** illustrating the trade-off between Speed (Time), Quality, and Cost (Money) in hiring:")

# Plot the triangle diagram
fig, ax = plt.subplots()
points = [(0, 0), (1, 0), (0.5, math.sqrt(3)/2)]
x, y = zip(*points)
# Draw triangle
ax.fill(x, y, "#ffffff20")  # translucent fill
ax.plot([points[0][0], points[1][0]], [points[0][1], points[1][1]], color="white")
ax.plot([points[1][0], points[2][0]], [points[1][1], points[2][1]], color="white")
ax.plot([points[2][0], points[0][0]], [points[2][1], points[0][1]], color="white")
# Label corners
ax.text(points[0][0] - 0.05, points[0][1] - 0.05, "Time (Speed)", color="white")
ax.text(points[1][0] + 0.02, points[1][1] - 0.05, "Money (Cost)", color="white")
ax.text(points[2][0] - 0.1, points[2][1] + 0.02, "Quality", color="white")
ax.axis('off')
st.pyplot(fig)

st.caption("**Figure:** In hiring, focusing on two aspects often means the third may require compromise. Vacalyzer helps push the boundaries of this triangle.")
st.write("""
**Why this matters:** A faster hiring process (Time) can save cost but might reduce candidate quality. 
Higher quality hires often take more time or resources. Vacalyser's automations enable you to **reduce time and cost** 
while maintaining high quality, effectively improving all three factors.
""")
st.write("""
By improving efficiency (less manual work, faster turnarounds) and enhancing quality (better job targeting and candidate experience), 
Vacalyser ultimately **boosts the return on investment** of your recruitment efforts.
""")
