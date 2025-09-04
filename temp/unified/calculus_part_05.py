from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class IntroductionToIntegration(Scene):
    def construct(self):
        # Title
        title = Text("Introduction to Integration", font_size=48)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))

        # Introduction to Integration
        axes = Axes(x_range=[-1, 3], y_range=[-1, 3], axis_config={"include_numbers": True})
        graph = axes.plot(lambda x: x**2, color=BLUE)
        tangent_line = axes.get_tangent_line(graph, graph.underlying_function, x=1)
        tangent_line.set_color(YELLOW)
        derivative_graph = axes.plot(lambda x: 2*x, color=GREEN)

        self.play(Create(axes), Create(graph))
        self.play(Create(tangent_line))
        self.wait(1)
        self.play(Transform(graph, derivative_graph))
        self.wait(2)
        self.play(FadeOut(axes), FadeOut(graph), FadeOut(tangent_line))

        # Understanding Antiderivatives
        axes = Axes(x_range=[-1, 3], y_range=[-1, 3], axis_config={"include_numbers": True})
        function_graph = axes.plot(lambda x: x**2, color=BLUE)
        antiderivative_graph = axes.plot(lambda x: (1/3)*x**3, color=ORANGE)

        self.play(Create(axes), Create(function_graph))
        self.wait(1)
        self.play(Transform(function_graph, antiderivative_graph))
        self.wait(2)
        self.play(FadeOut(axes), FadeOut(function_graph))

        # Power Rule for Integration
        equation = MathTex(r"\int x^n \, dx = \frac{x^{n+1}}{n+1} + C", font_size=36)
        self.play(Write(equation))
        self.wait(2)
        self.play(FadeOut(equation))

        # Example 1: Basic Antiderivative
        axes = Axes(x_range=[-1, 3], y_range=[-1, 3], axis_config={"include_numbers": True})
        function_graph = axes.plot(lambda x: x**2, color=BLUE)
        solution = MathTex(r"\int x^2 \, dx = \frac{x^3}{3} + C", font_size=36)

        self.play(Create(axes), Create(function_graph))
        self.wait(1)
        self.play(Write(solution))
        self.wait(2)
        self.play(FadeOut(axes), FadeOut(function_graph), FadeOut(solution))

        # Example 2: Antiderivative with a Fractional Power
        axes = Axes(x_range=[-1, 3], y_range=[-1, 3], axis_config={"include_numbers": True})
        function_graph = axes.plot(lambda x: x**0.5, color=BLUE)
        solution = MathTex(r"\int x^{1/2} \, dx = \frac{2}{3}x^{3/2} + C", font_size=36)

        self.play(Create(axes), Create(function_graph))
        self.wait(1)
        self.play(Write(solution))
        self.wait(2)
        self.play(FadeOut(axes), FadeOut(function_graph), FadeOut(solution))

        # Definite Integrals and Area Under a Curve
        axes = Axes(x_range=[0, 3], y_range=[0, 3], axis_config={"include_numbers": True})
        curve = axes.plot(lambda x: x**2, color=BLUE)
        area = axes.get_area(curve, x_range=[0, 2], color=GREY, opacity=0.5)
        integral = MathTex(r"\int_0^2 x^2 \, dx", font_size=36)

        self.play(Create(axes), Create(curve))
        self.play(Create(area))
        self.wait(1)
        self.play(Write(integral))
        self.wait(2)
        self.play(FadeOut(axes), FadeOut(curve), FadeOut(area), FadeOut(integral))

        # Applications of Integration in Physics
        axes = Axes(x_range=[0, 3], y_range=[0, 3], axis_config={"include_numbers": True})
        velocity_graph = axes.plot(lambda x: 2*x, color=BLUE)
        displacement_area = axes.get_area(velocity_graph, x_range=[0, 2], color=GREY, opacity=0.5)
        displacement_calc = MathTex(r"\int_0^2 2x \, dx", font_size=36)

        self.play(Create(axes), Create(velocity_graph))
        self.play(Create(displacement_area))
        self.wait(1)
        self.play(Write(displacement_calc))
        self.wait(2)
        self.play(FadeOut(axes), FadeOut(velocity_graph), FadeOut(displacement_area), FadeOut(displacement_calc))

        # Applications of Integration in Economics
        axes = Axes(x_range=[0, 3], y_range=[0, 3], axis_config={"include_numbers": True})
        cost_graph = axes.plot(lambda x: x + 1, color=BLUE)
        total_cost_area = axes.get_area(cost_graph, x_range=[0, 2], color=GREY, opacity=0.5)
        total_cost_calc = MathTex(r"\int_0^2 (x+1) \, dx", font_size=36)

        self.play(Create(axes), Create(cost_graph))
        self.play(Create(total_cost_area))
        self.wait(1)
        self.play(Write(total_cost_calc))
        self.wait(2)
        self.play(FadeOut(axes), FadeOut(cost_graph), FadeOut(total_cost_area), FadeOut(total_cost_calc))

        # Visualizing the Reverse Process of Differentiation
        axes = Axes(x_range=[-1, 3], y_range=[-1, 3], axis_config={"include_numbers": True})
        derivative_graph = axes.plot(lambda x: 2*x, color=GREEN)
        antiderivative_graph = axes.plot(lambda x: x**2, color=ORANGE)

        self.play(Create(axes), Create(derivative_graph))
        self.wait(1)
        self.play(Transform(derivative_graph, antiderivative_graph))
        self.wait(2)
        self.play(FadeOut(axes), FadeOut(derivative_graph))

        # Summary and Key Takeaways
        summary = VGroup(
            Text("Key Concepts:", font_size=36),
            Text("- Antiderivative: F'(x) = f(x)", font_size=32),
            Text("- Definite Integral: Area under curve", font_size=32),
            Text("- Power Rule: Reverse of differentiation", font_size=32)
        ).arrange(DOWN, aligned_edge=LEFT)

        self.play(Write(summary))
        self.wait(3)
        self.play(FadeOut(summary))

        # Closing Remarks
        closing_text = Text("Thank you for watching!", font_size=48)
        quote = Text("Integration: The art of summing infinitesimals.", font_size=32, color=GREY)

        self.play(Write(closing_text))
        self.wait(1)
        self.play(Write(quote))
        self.wait(3)
        self.play(FadeOut(closing_text), FadeOut(quote))