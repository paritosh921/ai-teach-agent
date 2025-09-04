from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class BasicDerivativeRules(Scene):
    def construct(self):
        # Introduction to Derivatives
        title = Text("Introduction to Derivatives", font_size=48)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))

        # Graph setup
        axes = Axes(
            x_range=[-1, 4, 1],
            y_range=[-1, 9, 1],
            axis_config={"include_numbers": True}
        )
        graph = axes.plot(lambda x: x**2, x_range=[-1, 3], color=BLUE)
        graph_label = axes.get_graph_label(graph, label="f(x) = x^2", x_val=2, direction=UP)

        # Secant line setup
        x_val = 1
        h_val = ValueTracker(1)
        secant_line = always_redraw(lambda: axes.get_secant_slope_group(
            x=x_val, graph=graph, dx=h_val.get_value(), secant_line_color=YELLOW, secant_line_length=4
        ))

        # Points on the graph
        point_a = always_redraw(lambda: Dot(axes.i2gp(x_val, graph), color=RED))
        point_b = always_redraw(lambda: Dot(axes.i2gp(x_val + h_val.get_value(), graph), color=RED))

        # Display graph and secant line
        self.play(Create(axes), Create(graph), Write(graph_label))
        self.play(Create(secant_line), FadeIn(point_a), FadeIn(point_b))
        self.wait(2)

        # Animate secant line moving as h decreases
        self.play(h_val.animate.set_value(0.1), run_time=4)
        self.wait(2)

        # From Secant to Tangent
        tangent_line = always_redraw(lambda: axes.get_tangent(
            graph=graph, x=x_val, length=4, color=GREEN
        ))

        # Transition from secant to tangent
        self.play(Transform(secant_line, tangent_line))
        self.wait(2)

        # Worked Example: f(x) = x²
        algebra_steps = MathTex(
            r"\text{Derivative: } \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}",
            r"= \lim_{h \to 0} \frac{(x+h)^2 - x^2}{h}",
            r"= \lim_{h \to 0} \frac{x^2 + 2xh + h^2 - x^2}{h}",
            r"= \lim_{h \to 0} \frac{2xh + h^2}{h}",
            r"= \lim_{h \to 0} (2x + h)",
            r"= 2x"
        ).arrange(DOWN, aligned_edge=LEFT).to_edge(RIGHT)

        # Display algebraic steps
        for step in algebra_steps:
            self.play(Write(step))
            self.wait(1)

        # Interpretation and Applications
        self.play(FadeOut(algebra_steps), FadeOut(axes), FadeOut(graph), FadeOut(secant_line), FadeOut(point_a), FadeOut(point_b))
        self.wait(1)

        # Understanding the Limit Process
        number_line = NumberLine(x_range=[-1, 1, 0.1], length=10, include_numbers=True)
        arrow = Arrow(start=number_line.n2p(0.5), end=number_line.n2p(0), buff=0, color=ORANGE)

        # Display number line and arrow
        self.play(Create(number_line), Create(arrow))
        self.wait(2)

        # Animate arrow moving towards zero
        self.play(arrow.animate.shift(LEFT * 5), run_time=4)
        self.wait(2)

        # Summary and Conclusion
        summary_table = Table(
            [["Concept", "Description"],
             ["Derivative", "Instantaneous rate of change"],
             ["Secant Line", "Average rate of change"],
             ["Tangent Line", "Instantaneous rate of change"]],
            col_labels=[Text("Key Concepts"), Text("Summary")],
            include_outer_lines=True
        ).scale(0.5).to_edge(UP)

        # Display summary table
        self.play(Create(summary_table))
        self.wait(2)

        # Final Thoughts and Next Steps
        resources = Text("Further Learning: Khan Academy, MIT OCW, Coursera", font_size=32).next_to(summary_table, DOWN)
        self.play(Write(resources))
        self.wait(2)

        # End Scene
        self.play(FadeOut(summary_table), FadeOut(resources), FadeOut(number_line), FadeOut(arrow))
        self.wait(2)