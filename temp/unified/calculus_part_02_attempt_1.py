from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class DerivativeAsLimit(Scene):
    def construct(self):
        # Introduction to Derivatives
        self.introduction_to_derivatives()
        self.wait(2)

        # Concept of Rate of Change
        self.concept_of_rate_of_change()
        self.wait(2)

        # Formal Definition
        self.formal_definition()
        self.wait(2)

        # Understanding Limits
        self.understanding_limits()
        self.wait(2)

        # Visualizing Derivatives
        self.visualizing_derivatives()
        self.wait(2)

        # Derivative of a Linear Function
        self.derivative_of_linear_function()
        self.wait(2)

        # Derivative of a Quadratic Function
        self.derivative_of_quadratic_function()
        self.wait(2)

        # Worked Examples
        self.worked_examples()
        self.wait(2)

        # Applications in Physics
        self.applications_in_physics()
        self.wait(2)

        # Applications in Economics
        self.applications_in_economics()
        self.wait(2)

        # Summary and Conclusion
        self.summary_and_conclusion()
        self.wait(2)

        # Q&A and Further Exploration
        self.qa_and_further_exploration()
        self.wait(2)

    def introduction_to_derivatives(self):
        car = SVGMobject("car.svg").scale(0.5).to_edge(LEFT)
        speedometer = SVGMobject("speedometer.svg").scale(0.5).to_edge(RIGHT)
        road = Line(LEFT, RIGHT).shift(DOWN)

        self.play(Create(road), FadeIn(car, shift=LEFT), FadeIn(speedometer, shift=RIGHT))
        self.play(car.animate.shift(RIGHT * 3), speedometer.animate.shift(LEFT * 3))
        self.wait()

    def concept_of_rate_of_change(self):
        axes = Axes(x_range=[0, 5, 1], y_range=[0, 5, 1], axis_config={"include_numbers": True})
        line = axes.plot(lambda x: x, x_range=[0, 4], color=BLUE)
        dot = Dot(axes.c2p(0, 0), color=RED)

        self.play(Create(axes), Create(line), FadeIn(dot))
        self.play(dot.animate.move_to(axes.c2p(4, 4)), run_time=3, rate_func=linear)
        self.wait()

    def formal_definition(self):
        formula = MathTex(r"f'(x) = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}", font_size=48)
        self.play(Write(formula))
        self.wait()

    def understanding_limits(self):
        number_line = NumberLine(x_range=[-3, 3, 1], length=10, include_numbers=True)
        arrows = VGroup(
            Arrow(start=number_line.n2p(-2), end=number_line.n2p(0), buff=0),
            Arrow(start=number_line.n2p(2), end=number_line.n2p(0), buff=0)
        )

        self.play(Create(number_line), Create(arrows))
        self.wait()

    def visualizing_derivatives(self):
        axes = Axes(x_range=[-1, 3, 1], y_range=[-1, 9, 1], axis_config={"include_numbers": True})
        graph = axes.plot(lambda x: x**2, x_range=[-1, 2], color=GREEN)
        tangent_line = axes.get_tangent_line(axes.input_to_graph_point(1, graph), graph, length=4)

        self.play(Create(axes), Create(graph))
        self.play(Create(tangent_line))
        self.wait()

    def derivative_of_linear_function(self):
        axes = Axes(x_range=[-1, 3, 1], y_range=[-1, 10, 1], axis_config={"include_numbers": True})
        line = axes.plot(lambda x: 3*x + 2, x_range=[-1, 2], color=YELLOW)

        self.play(Create(axes), Create(line))
        self.wait()

    def derivative_of_quadratic_function(self):
        axes = Axes(x_range=[-1, 3, 1], y_range=[-1, 9, 1], axis_config={"include_numbers": True})
        graph = axes.plot(lambda x: x**2, x_range=[-1, 2], color=GREEN)
        tangent_line = axes.get_tangent_line(axes.input_to_graph_point(1, graph), graph, length=4)

        self.play(Create(axes), Create(graph))
        self.play(Create(tangent_line))
        self.wait()

    def worked_examples(self):
        example_eq = MathTex(r"f(x) = 3x + 2", font_size=36).to_edge(LEFT)
        graph = Axes(x_range=[-1, 3, 1], y_range=[-1, 10, 1], axis_config={"include_numbers": True}).plot(lambda x: 3*x + 2, x_range=[-1, 2], color=YELLOW)

        self.play(Write(example_eq), Create(graph))
        self.wait()

    def applications_in_physics(self):
        axes = Axes(x_range=[0, 5, 1], y_range=[0, 5, 1], axis_config={"include_numbers": True})
        velocity_graph = axes.plot(lambda x: x, x_range=[0, 4], color=BLUE)
        acceleration_graph = axes.plot(lambda x: 2*x, x_range=[0, 4], color=RED)

        self.play(Create(axes), Create(velocity_graph), Create(acceleration_graph))
        self.wait()

    def applications_in_economics(self):
        axes = Axes(x_range=[0, 5, 1], y_range=[0, 5, 1], axis_config={"include_numbers": True})
        marginal_cost = axes.plot(lambda x: x**2, x_range=[0, 2], color=GREEN)
        marginal_revenue = axes.plot(lambda x: 4 - x, x_range=[0, 2], color=ORANGE)

        self.play(Create(axes), Create(marginal_cost), Create(marginal_revenue))
        self.wait()

    def summary_and_conclusion(self):
        bullet_points = VGroup(
            Text("Key Takeaways:", font_size=36),
            Text("- Derivative as a limit", font_size=32),
            Text("- Slope of tangent line", font_size=32),
            Text("- Applications in real life", font_size=32)
        ).arrange(DOWN, aligned_edge=LEFT).to_edge(LEFT)

        self.play(Write(bullet_points))
        self.wait()

    def qa_and_further_exploration(self):
        question_mark = Text("?", font_size=72).to_edge(UP)
        topics = VGroup(
            Text("Further Topics:", font_size=36),
            Text("- Higher Order Derivatives", font_size=32),
            Text("- Partial Derivatives", font_size=32),
            Text("- Derivatives in Complex Analysis", font_size=32)
        ).arrange(DOWN, aligned_edge=LEFT).to_edge(LEFT)

        self.play(Write(question_mark), Write(topics))
        self.wait()