# src/utils/visualization.py
import matplotlib.pyplot as plt
import streamlit as st

def plot_responsibility_triangle(technical, managerial, administrative):
    """
    Draw a triangle showing responsibilities distribution.
    """
    # Coordinates of triangle corners
    X = [0, 1, 0.5, 0]
    Y = [0, 0, 0.866, 0]  # 0.866 ~ sqrt(3)/2 for equilateral triangle
    
    fig, ax = plt.subplots()
    ax.plot(X, Y, color="black")
    ax.text(0, -0.05, f"{managerial}", ha='center', va='top')
    ax.text(1, -0.05, f"{technical}", ha='center', va='top')
    ax.text(0.5, 0.866+0.05, f"{administrative}", ha='center', va='bottom')
    ax.axis('off')
    st.pyplot(fig)
