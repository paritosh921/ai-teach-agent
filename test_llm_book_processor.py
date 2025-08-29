#!/usr/bin/env python3
"""
Test script for the new LLM-powered book processor

This demonstrates the intelligent content extraction capabilities
that work with any text format, not just structured documents.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_llm_book_processor():
    """Test the LLM-powered book processor"""

    print("🧪 Testing LLM-Powered Book Processor")
    print("=" * 60)

    try:
        from src.llm_book_processor import LLMBookProcessor
        from src.llm_book_adapter import LLMBasedBookProcessor

        # Check if API key is available
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY not found in environment variables")
            print("Please set it with: export OPENAI_API_KEY='your-key-here'")
            return False

        print(f"✅ OpenAI API key found")

        # Initialize processors
        llm_processor = LLMBookProcessor(api_key)
        enhanced_processor = LLMBasedBookProcessor()

        print("✅ LLM processors initialized successfully")

        # Test with sample content
        sample_content = """
        # Understanding Machine Learning

        Machine learning is a subset of artificial intelligence that enables computers to learn without being explicitly programmed. Instead of writing detailed instructions for every possible scenario, we provide algorithms that can learn patterns from data.

        ## What is Machine Learning?

        At its core, machine learning involves three main components:
        1. Data - The fuel for learning
        2. Algorithms - The methods for learning
        3. Models - The result of learning

        The basic idea is simple: show a computer lots of examples, and let it figure out the patterns. This is similar to how humans learn.

        ## Types of Machine Learning

        ### Supervised Learning
        In supervised learning, we have labeled training data. The algorithm learns to map inputs to outputs based on example input-output pairs.

        For example, if we want to predict house prices, we might have data like:
        - House size: 2000 sq ft, Price: $300,000
        - House size: 1500 sq ft, Price: $250,000

        The algorithm learns the relationship between size and price.

        ### Unsupervised Learning
        Unsupervised learning finds hidden patterns in data without labeled examples. It's like exploring a new city without a map - you discover neighborhoods and landmarks on your own.

        Common applications include:
        - Customer segmentation
        - Anomaly detection
        - Recommendation systems

        ## Key Concepts

        **Overfitting**: When a model learns the training data too well, including noise and outliers. It's like memorizing answers instead of understanding concepts.

        **Underfitting**: When a model is too simple to capture the underlying patterns. It's like trying to understand quantum physics with basic arithmetic.

        **Bias-Variance Tradeoff**: The balance between model simplicity and complexity. Too simple (high bias) misses important patterns. Too complex (high variance) overfits to noise.

        ## Applications

        Machine learning powers many modern technologies:

        1. **Image Recognition** - Facebook's photo tagging, self-driving cars
        2. **Natural Language Processing** - ChatGPT, Google Translate
        3. **Recommendation Systems** - Netflix suggestions, Amazon recommendations
        4. **Medical Diagnosis** - Cancer detection, drug discovery
        5. **Financial Trading** - Algorithmic trading, fraud detection

        ## Getting Started

        To begin with machine learning:

        1. Learn Python programming
        2. Study linear algebra and statistics
        3. Practice with datasets from Kaggle
        4. Build projects and experiment

        Remember: machine learning is more art than science. It requires creativity, experimentation, and persistence.

        The future belongs to those who can teach machines to learn.
        """

        print("\n📖 Processing sample machine learning content with LLM...")

        # Process with LLM
        llm_book = llm_processor.process_raw_content(sample_content, "machine_learning")

        print(f"✅ Processed successfully!")
        print(f"📚 Title: {llm_book.title}")
        print(f"🎯 Difficulty: {llm_book.overall_difficulty}")
        print(f"👥 Audience: {llm_book.target_audience}")
        print(f"📑 Sections: {llm_book.total_sections}")

        print(f"\n📋 Chapter Structure:")
        for i, chapter in enumerate(llm_book.chapters, 1):
            print(f"  {i}. {chapter.title} (Level {chapter.level})")

        print(f"\n📋 All Sections:")
        for i, section in enumerate(llm_book.sections, 1):
            print(f"  {i}. {section.title}")
            if section.educational_concepts:
                print(f"     🔍 Concepts: {len(section.educational_concepts)}")
            if section.key_formulas:
                print(f"     📐 Formulas: {len(section.key_formulas)}")
            if section.visual_elements:
                print(f"     👁️ Visuals: {len(section.visual_elements)}")

        print(f"\n🎯 Learning Objectives Found:")
        total_objectives = sum(len(s.learning_objectives) for s in llm_book.sections)
        print(f"  Total learning objectives: {total_objectives}")

        # Show sample concepts from first section
        if llm_book.sections and llm_book.sections[0].educational_concepts:
            sample_concept = llm_book.sections[0].educational_concepts[0]
            print(f"\n💡 Sample Concept:")
            print(f"  Name: {sample_concept.name}")
            print(f"  Definition: {sample_concept.definition[:100]}...")
            print(f"  Difficulty: {sample_concept.difficulty_level}")
            if sample_concept.examples:
                print(f"  Examples: {len(sample_concept.examples)}")

        # Test backward compatibility
        print(f"\n🔄 Testing backward compatibility...")
        traditional_book = enhanced_processor._convert_llm_to_traditional(llm_book)

        print(f"✅ Traditional format conversion successful")
        print(f"📚 Traditional title: {traditional_book.title}")
        print(f"📑 Traditional sections: {traditional_book.total_sections}")

        # Test with actual book file
        print(f"\n📖 Testing with actual book file...")
        if os.path.exists("books/calculus.txt"):
            try:
                file_book = llm_processor.process_book_file("books/calculus.txt", "calculus")
                print(f"✅ Successfully processed calculus.txt")
                print(f"📚 Title: {file_book.title}")
                print(f"📑 Sections: {file_book.total_sections}")

                # Save processed version
                cache_path = "cache/llm_books/calculus_llm.json"
                os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                llm_processor.save_processed_book(file_book, cache_path)
                print(f"💾 Saved processed book to {cache_path}")

            except Exception as e:
                print(f"⚠️ File processing failed: {e}")
        else:
            print("ℹ️ calculus.txt not found, skipping file test")

        print(f"\n🎉 LLM Book Processor Test Completed Successfully!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def demonstrate_flexibility():
    """Demonstrate the flexibility of LLM processing with different formats"""

    print("\n🎭 Demonstrating Format Flexibility")
    print("=" * 50)

    try:
        from src.llm_book_processor import LLMBookProcessor

        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY required for demonstration")
            return

        processor = LLMBookProcessor(api_key)

        # Test with different formats
        test_formats = [
            {
                "name": "Markdown Format",
                "content": """
# Quantum Physics Basics

## Wave-Particle Duality

Light behaves as both waves and particles. This dual nature is called wave-particle duality.

### Key Experiments
1. **Double-slit experiment** - Shows interference patterns
2. **Photoelectric effect** - Demonstrates particle nature

**Einstein's explanation**: E = hν, where h is Planck's constant.

Applications: Lasers, solar panels, medical imaging.
                """
            },
            {
                "name": "Plain Text Format",
                "content": """
Organic Chemistry Introduction

Carbon compounds are the basis of life. Carbon atoms can form four bonds, creating complex molecules.

Key concepts:
- Bonding: Carbon forms covalent bonds
- Isomers: Same formula, different structure
- Functional groups: Determine chemical properties

Examples include alkanes, alkenes, alcohols, and carboxylic acids.

The study of organic chemistry helps us understand:
1. How drugs work
2. Why plastics behave certain ways
3. How living organisms function
                """
            },
            {
                "name": "Lecture Notes Style",
                "content": """
Lecture 3: Thermodynamics

First Law: Energy conservation
ΔU = Q - W

Where:
U = internal energy
Q = heat added
W = work done

Second Law: Entropy increases
ΔS ≥ 0 for isolated systems

Applications:
- Heat engines
- Refrigerators
- Chemical reactions

Homework: Problems 5.1, 5.3, 5.7
                """
            }
        ]

        for i, test_format in enumerate(test_formats, 1):
            print(f"\n{i}. Processing {test_format['name']}...")
            try:
                result = processor.process_raw_content(test_format['content'], f"test_topic_{i}")

                print(f"   ✅ Title: {result.title}")
                print(f"   📑 Sections: {result.total_sections}")
                print(f"   🎯 Difficulty: {result.overall_difficulty}")

                if result.sections:
                    first_section = result.sections[0]
                    print(f"   💡 Concepts found: {len(first_section.educational_concepts)}")
                    print(f"   📐 Formulas found: {len(first_section.key_formulas)}")

            except Exception as e:
                print(f"   ❌ Failed: {e}")

        print(f"\n🎉 Format flexibility demonstration completed!")

    except Exception as e:
        print(f"❌ Demonstration failed: {e}")

if __name__ == "__main__":
    success = test_llm_book_processor()
    if success:
        demonstrate_flexibility()
