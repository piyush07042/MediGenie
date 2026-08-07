export type Guideline = {
  source: string;
  year?: string | number;
  bullets: string[];
};

const GUIDELINES: Record<string, Guideline> = {
  ADA: {
    source: "ADA",
    year: "2025",
    bullets: [
      "HbA1c >6.5%",
      "Recommend lifestyle intervention",
      "Annual retinal exam",
      "Kidney screening",
    ],
  },
  // Add more guideline entries here as needed (KDIGO, AHA, WHO, etc.)
};

export function getGuidelineFor(disease: string | undefined | null) {
  if (!disease) return null;
  const key = disease.toLowerCase();

  // Simple heuristic mapping for now
  if (key.includes("diabetes") || key.includes("diabetic") || key.includes("hba1c")) {
    return GUIDELINES.ADA;
  }

  return null;
}

export default GUIDELINES;
