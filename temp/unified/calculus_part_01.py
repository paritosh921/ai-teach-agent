from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class UnderstandingLimits(Scene):
    def construct(self):
        # Introduction to Limits
        self.introduction_to_limits()

        # Graphical Representation
        self.graphical_representation()

        # Epsilon-Delta Definition
        self.epsilon_delta_definition()

        # Limit Laws Introduction
        self.limit_laws_introduction()

        # Example 1: Basic Limit Calculation
        self.example_basic_limit_calculation()

        # Example 2: Applying Limit Laws
        self.example_applying_limit_laws()

        # Common Misconceptions
        self.common_misconceptions()

        # Application in Physics
        self.application_in_physics()

        # Visualizing Epsilon-Delta
        self.visualizing_epsilon_delta()

        # Summary of Limit Concepts
        self.summary_of_limit_concepts()

        # Interactive Quiz
        self.interactive_quiz()

        # Closing Remarks
        self.closing_remarks()

    def introduction_to_limits(self):
        road = Line(LEFT * 5, RIGHT * 5)
        car = Dot(color=BLUE).move_to(LEFT * 4.5)
        city = Text("Destination", font_size=32).next_to(road, UP, buff=0.5)

        self.play(Create(road), Write(city))
        self.play(car.animate.move_to(RIGHT * 4.5), run_time=4)
        self.wait()

    def graphical_representation(self):
        axes = Axes(x_range=[0, 4, 1], y_range=[0, 16, 4], axis_config={"include_numbers": True})
        graph = axes.plot(lambda x: x**2, x_range=[0, 4], color=GREEN)
        point = Dot(axes.coords_to_point(2, 4), color=RED)
        label = MathTex("(2, 4)", font_size=32).next_to(point, UP)

        self.play(Create(axes), Create(graph))
        self.play(axes.animate.scale(1.5).move_to(ORIGIN))
        self.play(FadeIn(point), Write(label))
        self.wait()

    def epsilon_delta_definition(self):
        number_line = NumberLine(x_range=[-1, 3, 1], length=10, include_numbers=True)
        delta_region = Rectangle(width=2, height=0.5, color=YELLOW, fill_opacity=0.5).move_to(number_line.n2p(1))
        epsilon_region = Rectangle(width=0.5, height=2, color=RED, fill_opacity=0.5).move_to(number_line.n2p(2))

        self.play(Create(number_line))
        self.play(FadeIn(delta_region), FadeIn(epsilon_region))
        self.wait()

    def limit_laws_introduction(self):
        sum_law = MathTex(r"\lim_{x \to a} (f(x) + g(x)) = \lim_{x \to a} f(x) + \lim_{x \to a} g(x)", font_size=32)
        product_law = MathTex(r"\lim_{x \to a} (f(x) \cdot g(x)) = \lim_{x \to a} f(x) \cdot \lim_{x \to a} g(x)", font_size=32)
        quotient_law = MathTex(r"\lim_{x \to a} \frac{f(x)}{g(x)} = \frac{\lim_{x \to a} f(x)}{\lim_{x \to a} g(x)}", font_size=32)

        self.play(Write(sum_law))
        self.wait()
        self.play(Transform(sum_law, product_law))
        self.wait()
        self.play(Transform(sum_law, quotient_law))
        self.wait()

    def example_basic_limit_calculation(self):
        step1 = MathTex(r"\lim_{x \to 2} x^2", font_size=32)
        step2 = MathTex(r"x^2 \to 4 \text{ as } x \to 2", font_size=32).next_to(step1, DOWN)
        step3 = MathTex(r"\lim_{x \to 2} x^2 = 4", font_size=32).next_to(step2, DOWN)

        self.play(Write(step1))
        self.wait()
        self.play(Write(step2))
        self.wait()
        self.play(Write(step3))
        self.wait()

    def example_applying_limit_laws(self):
        step1 = MathTex(r"\lim_{x \to 3} (2x + 1)", font_size=32)
        step2 = MathTex(r"= 2 \cdot \lim_{x \to 3} x + \lim_{x \to 3} 1", font_size=32).next_to(step1, DOWN)
        step3 = MathTex(r"= 2 \cdot 3 + 1 = 7", font_size=32).next_to(step2, DOWN)

        self.play(Write(step1))
        self.wait()
        self.play(Write(step2))
        self.wait()
        self.play(Write(step3))
        self.wait()

    def common_misconceptions(self):
        axes = Axes(x_range=[0, 4, 1], y_range=[0, 4, 1], axis_config={"include_numbers": True})
        discontinuous_graph = axes.plot(lambda x: 1 if x != 2 else 3, x_range=[0, 4], color=GREEN)
        discontinuity = Dot(axes.coords_to_point(2, 1), color=RED)
        limit_value = Dot(axes.coords_to_point(2, 3), color=YELLOW)

        self.play(Create(axes), Create(discontinuous_graph))
        self.play(FadeIn(discontinuity), FadeIn(limit_value))
        self.wait()

    def application_in_physics(self):
        axes = Axes(x_range=[0, 4, 1], y_range=[0, 4, 1], axis_config={"include_numbers": True})
        velocity_graph = axes.plot(lambda x: x, x_range=[0, 4], color=BLUE)
        tangent_line = DashedLine(axes.coords_to_point(2, 2), axes.coords_to_point(3, 3), color=RED)

        self.play(Create(axes), Create(velocity_graph))
        self.play(Create(tangent_line))
        self.wait()

    def visualizing_epsilon_delta(self):
        number_line = NumberLine(x_range=[-1, 3, 1], length=10, include_numbers=True)
        delta_region = Rectangle(width=2, height=0.5, color=YELLOW, fill_opacity=0.5).move_to(number_line.n2p(1))
        epsilon_region = Rectangle(width=0.5, height=2, color=RED, fill_opacity=0.5).move_to(number_line.n2p(2))

        self.play(Create(number_line))
        self.play(delta_region.animate.scale(0.5), epsilon_region.animate.scale(0.5))
        self.wait()

    def summary_of_limit_concepts(self):
        summary = VGroup(
            Text("Key Concepts of Limits:", font_size=36),
            Text("- Intuitive Understanding", font_size=32),
            Text("- Epsilon-Delta Definition", font_size=32),
            Text("- Limit Laws", font_size=32),
            Text("- Common Misconceptions", font_size=32)
        ).arrange(DOWN, aligned_edge=LEFT)

        self.play(FadeIn(summary[0]))
        self.wait()
        for line in summary[1:]:
            self.play(FadeIn(line))
            self.wait()

    def interactive_quiz(self):
        question = Text("What is the limit of x^2 as x approaches 2?", font_size=32)
        options = VGroup(
            Text("A) 2", font_size=32),
            Text("B) 4", font_size=32),
            Text("C) 0", font_size=32),
            Text("D) Does not exist", font_size=32)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5).next_to(question, DOWN)

        self.play(Write(question))
        self.wait()
        self.play(FadeIn(options))
        self.wait()
        correct_answer = Text("Correct Answer: B) 4", font_size=32, color=GREEN).next_to(options, DOWN)
        self.play(Write(correct_answer))
        self.wait()

    def closing_remarks(self):
        thank_you = Text("Thank you for watching!", font_size=36)
        further_study = Text("Explore more on derivatives and integrals.", font_size=32).next_to(thank_you, DOWN)

        self.play(FadeIn(thank_you))
        self.wait()
        self.play(FadeIn(further_study))
        self.wait()