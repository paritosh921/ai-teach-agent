from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class IntroductionToDerivatives(Scene):
    def construct(self):
        # Title
        title = Text("Introduction to Derivatives")
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))

        # Scene 1: Car and Speedometer
        car = Text('diagram', font_size=36).scale(0.5).to_edge(LEFT)
        speedometer = Text('diagram', font_size=36).scale(0.5).to_edge(RIGHT)
        self.play(FadeIn(car), FadeIn(speedometer))
        self.wait(1)
        self.play(car.animate.shift(RIGHT * 4), speedometer.animate.rotate(PI / 4))
        self.wait(2)
        self.play(FadeOut(car), FadeOut(speedometer))

        # Scene 2: Graph of Distance vs. Time
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            axis_config={"include_numbers": True}
        )
        graph = axes.plot(lambda x: 0.5 * x**2, x_range=[0, 10], color=BLUE)
        tangent_line = axes.get_tangent_line(graph, 5, color=YELLOW)
        self.play(Create(axes), Create(graph))
        self.wait(1)
        self.play(Create(tangent_line))
        self.wait(2)
        self.play(FadeOut(axes), FadeOut(graph), FadeOut(tangent_line))

        # Scene 3: Formal Definition of Derivative
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            axis_config={"include_numbers": True}
        )
        graph = axes.plot(lambda x: x**2, x_range=[0, 10], color=GREEN)
        point = Dot(axes.c2p(5, 25), color=RED)
        tangent_line = axes.get_tangent_line(graph, 5, color=YELLOW)
        limit_formula = MathTex(
            r"f'(x) = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}",
            font_size=32
        ).to_edge(DOWN)
        self.play(Create(axes), Create(graph), FadeIn(point))
        self.wait(1)
        self.play(Create(tangent_line))
        self.wait(1)
        self.play(Write(limit_formula))
        self.wait(2)
        self.play(FadeOut(axes), FadeOut(graph), FadeOut(point), FadeOut(tangent_line), FadeOut(limit_formula))

        # Scene 4: Visualizing Limits
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            axis_config={"include_numbers": True}
        )
        graph = axes.plot(lambda x: 1 / (x - 5) + 5, x_range=[0.5, 9.5], color=ORANGE)
        limit_line = DashedLine(axes.c2p(5, 0), axes.c2p(5, 10), color=RED)
        self.play(Create(axes), Create(graph))
        self.wait(1)
        self.play(Create(limit_line))
        self.wait(2)
        self.play(FadeOut(axes), FadeOut(graph), FadeOut(limit_line))

        # Scene 5: Worked Example - Linear Function
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            axis_config={"include_numbers": True}
        )
        linear_graph = axes.plot(lambda x: 2 * x + 1, x_range=[0, 10], color=BLUE)
        derivative_line = axes.plot(lambda x: 2, x_range=[0, 10], color=YELLOW)
        self.play(Create(axes), Create(linear_graph))
        self.wait(1)
        self.play(Create(derivative_line))
        self.wait(2)
        self.play(FadeOut(axes), FadeOut(linear_graph), FadeOut(derivative_line))

        # Scene 6: Worked Example - Quadratic Function
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 100, 10],
            axis_config={"include_numbers": True}
        )
        quadratic_graph = axes.plot(lambda x: x**2, x_range=[0, 10], color=GREEN)
        derivative_curve = axes.plot(lambda x: 2 * x, x_range=[0, 10], color=YELLOW)
        self.play(Create(axes), Create(quadratic_graph))
        self.wait(1)
        self.play(Create(derivative_curve))
        self.wait(2)
        self.play(FadeOut(axes), FadeOut(quadratic_graph), FadeOut(derivative_curve))

        # Scene 7: Comparing Linear and Quadratic Derivatives
        axes1 = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            axis_config={"include_numbers": True}
        ).to_edge(LEFT)
        linear_graph = axes1.plot(lambda x: 2 * x + 1, x_range=[0, 10], color=BLUE)
        derivative_line = axes1.plot(lambda x: 2, x_range=[0, 10], color=YELLOW)

        axes2 = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 100, 10],
            axis_config={"include_numbers": True}
        ).to_edge(RIGHT)
        quadratic_graph = axes2.plot(lambda x: x**2, x_range=[0, 10], color=GREEN)
        derivative_curve = axes2.plot(lambda x: 2 * x, x_range=[0, 10], color=YELLOW)

        self.play(Create(axes1), Create(linear_graph), Create(derivative_line))
        self.play(Create(axes2), Create(quadratic_graph), Create(derivative_curve))
        self.wait(2)
        self.play(FadeOut(axes1), FadeOut(linear_graph), FadeOut(derivative_line), FadeOut(axes2), FadeOut(quadratic_graph), FadeOut(derivative_curve))

        # Scene 8: Applications in Physics
        moving_object = Dot().to_edge(LEFT)
        velocity_vector = Arrow(moving_object.get_center(), moving_object.get_center() + RIGHT, buff=0, color=BLUE)
        acceleration_vector = Arrow(moving_object.get_center(), moving_object.get_center() + RIGHT * 0.5, buff=0, color=RED)
        self.play(FadeIn(moving_object), GrowArrow(velocity_vector))
        self.wait(1)
        self.play(moving_object.animate.shift(RIGHT * 4), velocity_vector.animate.shift(RIGHT * 4))
        self.wait(1)
        self.play(GrowArrow(acceleration_vector))
        self.wait(2)
        self.play(FadeOut(moving_object), FadeOut(velocity_vector), FadeOut(acceleration_vector))

        # Scene 9: Derivatives in Economics
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            axis_config={"include_numbers": True}
        )
        supply_graph = axes.plot(lambda x: 0.5 * x + 2, x_range=[0, 10], color=BLUE)
        demand_graph = axes.plot(lambda x: -0.5 * x + 8, x_range=[0, 10], color=GREEN)
        tangent_line_supply = axes.get_tangent_line(supply_graph, 4, color=YELLOW)
        tangent_line_demand = axes.get_tangent_line(demand_graph, 6, color=YELLOW)
        self.play(Create(axes), Create(supply_graph), Create(demand_graph))
        self.wait(1)
        self.play(Create(tangent_line_supply), Create(tangent_line_demand))
        self.wait(2)
        self.play(FadeOut(axes), FadeOut(supply_graph), FadeOut(demand_graph), FadeOut(tangent_line_supply), FadeOut(tangent_line_demand))

        # Scene 10: Derivatives in Biology
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 100, 10],
            axis_config={"include_numbers": True}
        )
        growth_curve = axes.plot(lambda x: 10 * x, x_range=[0, 10], color=GREEN)
        tangent_line = axes.get_tangent_line(growth_curve, 5, color=YELLOW)
        self.play(Create(axes), Create(growth_curve))
        self.wait(1)
        self.play(Create(tangent_line))
        self.wait(2)
        self.play(FadeOut(axes), FadeOut(growth_curve), FadeOut(tangent_line))

        # Scene 11: Advanced Derivative Techniques
        chain_rule_example = MathTex(
            r"\frac{d}{dx}[\sin(x^2)] = 2x\cos(x^2)",
            font_size=32
        ).to_edge(UP)
        product_rule_example = MathTex(
            r"\frac{d}{dx}[uv] = u'v + uv'",
            font_size=32
        ).to_edge(DOWN)
        self.play(Write(chain_rule_example))
        self.wait(1)
        self.play(Write(product_rule_example))
        self.wait(2)
        self.play(FadeOut(chain_rule_example), FadeOut(product_rule_example))

        # Scene 12: Conclusion and Summary
        key_concepts = VGroup(
            Text("Key Concepts:"),
            Text("- Derivative as rate of change"),
            Text("- Limit definition"),
            Text("- Applications in various fields")
        ).arrange(DOWN, aligned_edge=LEFT).to_edge(LEFT)
        formulas = VGroup(
            MathTex(r"f'(x) = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}", font_size=32),
            MathTex(r"\frac{d}{dx}[uv] = u'v + uv'", font_size=32)
        ).arrange(DOWN, aligned_edge=LEFT).to_edge(RIGHT)
        self.play(FadeIn(key_concepts))
        self.wait(1)
        self.play(FadeIn(formulas))
        self.wait(2)
        self.play(FadeOut(key_concepts), FadeOut(formulas))
        self.wait(2)