import React from 'react';

interface Category {
    title: string;
    icon: string;
    questions: string[];
}

const categories: Category[] = [
    {
        title: "Fund Overview",
        icon: "📊",
        questions: [
            "What is the NAV of the fund?",
            "Who manages this mutual fund?",
            "What is the benchmark index?"
        ]
    },
    {
        title: "Costs & Charges",
        icon: "💰",
        questions: [
            "What is the expense ratio?",
            "What is the exit load?",
            "What are the fund charges?"
        ]
    },
    {
        title: "SIP & Investment",
        icon: "📈",
        questions: [
            "What is the minimum SIP amount?",
            "What is the minimum lump sum investment?"
        ]
    },
    {
        title: "Risk & Benchmark",
        icon: "🛡️",
        questions: [
            "What does the riskometer indicate?",
            "What is the benchmark index?"
        ]
    },
    {
        title: "Lock-in & Tax",
        icon: "🔒",
        questions: [
            "What is the lock-in period for ELSS?",
            "What are the tax benefits of ELSS?"
        ]
    }
];

interface QuestionCategoriesProps {
    onSelectQuestion: (question: string) => void;
}

export default function QuestionCategories({ onSelectQuestion }: QuestionCategoriesProps) {
    return (
        <div className="space-y-6">
            <div className="px-2">
                <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                    <span className="text-lg">💡</span> What Can I Ask?
                </h4>
                <p className="text-[10px] text-gray-500 font-medium mt-1">
                    Explore factual categories to get the most accurate information.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {categories.map((category, idx) => (
                    <div key={idx} className="bg-white rounded-3xl p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
                        <div className="flex items-center gap-3 mb-4">
                            <span className="text-xl bg-gray-50 w-10 h-10 flex items-center justify-center rounded-xl">
                                {category.icon}
                            </span>
                            <h5 className="font-bold text-gray-800 text-sm">{category.title}</h5>
                        </div>
                        <div className="flex flex-wrap gap-2">
                            {category.questions.map((q, qIdx) => (
                                <button
                                    key={qIdx}
                                    onClick={() => onSelectQuestion(q)}
                                    className="text-left py-2 px-3 bg-[#f8f9fa] hover:bg-[#00d09c]/10 hover:text-[#008d6a] rounded-xl text-[11px] font-semibold text-gray-600 border border-transparent hover:border-[#00d09c]/20 transition-all leading-tight"
                                >
                                    {q}
                                </button>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
