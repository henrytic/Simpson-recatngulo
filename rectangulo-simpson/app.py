from flask import Flask, request, render_template
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from sympy import symbols, sympify, lambdify

app = Flask(__name__)

def plot_to_img(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return image_base64

def simpson_rule(func, a, b, n):
    """Regla de Simpson para integrar 'func' desde 'a' hasta 'b' con 'n' subintervalos"""
    if n % 2 != 0:
        raise ValueError("El número de subintervalos 'n' debe ser par.")

    x = symbols('x')
    f = lambdify(x, sympify(func), 'numpy')

    dx = (b - a) / n
    x_vals = np.linspace(a, b, n + 1)
    y_vals = f(x_vals)

    integral = dx/3 * np.sum(y_vals[0:-1:2] + 4*y_vals[1::2] + y_vals[2::2])

    # Preparación del gráfico
    fig, ax = plt.subplots()

    # Dibujar las áreas de aproximación de Simpson primero
    area_color = '#2ca02c'  # Verde
    area_alpha = 0.5  # Semi-transparencia
    for i in range(0, n, 2):
        xs = np.linspace(x_vals[i], x_vals[i + 2], 100)
        ys = f(xs)
        ax.fill_between(xs, ys, color=area_color, alpha=area_alpha)

    # Luego dibujar la función
    x_smooth = np.linspace(a, b, 300)
    y_smooth = f(x_smooth)
    ax.plot(x_smooth, y_smooth, label='Función f(x)', color='blue', linewidth=2)

    ax.set_title('Aproximación de la Integral usando el Método de Simpson')
    ax.set_xlabel('x')
    ax.set_ylabel('f(x)')
    ax.legend()

    plot_url = plot_to_img(fig)
    plt.close()

    return integral, plot_url

#---------------------------------------

def metodo_rectangulo(func, a, b, n, metodo):
    """Método del Rectángulo para integrar 'func' desde 'a' hasta 'b' con 'n' subintervalos"""
    x = symbols('x')
    f = lambdify(x, sympify(func), 'numpy')

    dx = (b - a) / n
    x_vals = np.linspace(a, b, n + 1)
    y_vals = f(x_vals)

    if metodo == 'izquierdo':
        integral = dx * np.sum(y_vals[:-1])
    elif metodo == 'derecho':
        integral = dx * np.sum(y_vals[1:])
    elif metodo == 'punto_medio':
        mid_points = (x_vals[:-1] + x_vals[1:]) / 2
        integral = dx * np.sum(f(mid_points))

    # Preparación del gráfico
    fig, ax = plt.subplots()
    
    # Primero dibujar los rectángulos
    for i in range(n):
        if metodo == 'izquierdo':
            rect_x = x_vals[i]
        elif metodo == 'derecho':
            rect_x = x_vals[i+1]
        elif metodo == 'punto_medio':
            rect_x = (x_vals[i] + x_vals[i+1]) / 2
            rect_width = dx
        else:
            raise ValueError("Método desconocido")

        rect_height = f(rect_x)
        rect = plt.Rectangle((x_vals[i], 0), dx, rect_height, color='orange', alpha=0.5)
        ax.add_patch(rect)

    # Luego dibujar la función
    x_smooth = np.linspace(a, b, 300)
    y_smooth = f(x_smooth)
    ax.plot(x_smooth, y_smooth, label='Función f(x)', color='blue')

    ax.set_title(f'Aproximación de la Integral usando el Método del Rectángulo ({metodo.title()})')
    ax.set_xlabel('x')
    ax.set_ylabel('f(x)')
    ax.legend()

    plot_url = plot_to_img(fig)
    plt.close()

    return integral, plot_url



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/simpson', methods=['GET', 'POST'])
def simpson():
    if request.method == 'POST':
        func = request.form.get('function')
        a = float(request.form.get('a'))
        b = float(request.form.get('b'))
        n = int(request.form.get('n'))

        try:
            result, plot_url = simpson_rule(func, a, b, n)
            return render_template('result.html', result=result, plot_url=plot_url)
        except Exception as e:
            error = f"Error al calcular la integral: {e}"
            return render_template('simpson.html', error=error)

    return render_template('simpson.html')

@app.route('/rectangulos', methods=['GET', 'POST'])
def rectangulos():
    if request.method == 'POST':
        func = request.form.get('function')
        a = float(request.form.get('a'))
        b = float(request.form.get('b'))
        n = int(request.form.get('n'))
        metodo = request.form.get('metodo')

        try:
            result, plot_url = metodo_rectangulo(func, a, b, n, metodo)
            return render_template('result.html', result=result, plot_url=plot_url)
        except Exception as e:
            error = f"Error al calcular la integral: {e}"
            return render_template('rectangulos.html', error=error)

    return render_template('rectangulos.html')

if __name__ == '__main__':
    app.run(debug=True)
