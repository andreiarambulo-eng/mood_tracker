export interface User {
  user_id: string;
  email: string;
  full_name: string;
  role: "Admin" | "User";
}

export interface MoodEntry {
  _id: string;
  user_id: string;
  mood_score: number;
  mood_label: string;
  remark: string | null;
  sentiment_score: number;
  sentiment_label: string;
  logged_date: string;
  created_at: string;
  updated_at: string;
}

export interface HeatmapEntry {
  date: string;
  mood_score: number;
  mood_label: string;
}

export interface WordCloudEntry {
  word: string;
  count: number;
}

export interface SentimentTrendEntry {
  date: string;
  sentiment_score: number;
  sentiment_label: string;
  mood_score: number;
}

export interface WeeklySummary {
  year: number;
  week: number;
  week_start: string;
  week_end: string;
  total_entries: number;
  average_mood: number | null;
  average_sentiment: number | null;
  most_common_mood: string | null;
  days: {
    date: string;
    mood_score: number;
    mood_label: string;
    sentiment_score: number;
    remark_preview: string | null;
  }[];
}

export interface MoodDistribution {
  mood_score: number;
  mood_label: string;
  count: number;
}

export interface ApiResponse<T = unknown> {
  success: boolean;
  message: string;
  data: T;
}

export interface PaginatedResponse<T = unknown> {
  success: boolean;
  message: string;
  data: {
    data: T[];
    pagination: {
      page: number;
      limit: number;
      total_count: number;
      total_pages: number;
      has_next: boolean;
      has_prev: boolean;
    };
  };
}

export const MOOD_EMOJIS: Record<number, string> = {
  1: "😢",
  2: "😟",
  3: "😐",
  4: "😊",
  5: "😄",
};

export const MOOD_COLORS: Record<number, string> = {
  1: "#ef4444",
  2: "#f97316",
  3: "#eab308",
  4: "#84cc16",
  5: "#22c55e",
};
