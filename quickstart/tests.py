def get_language_and_sentiment(self):
    self.language = detect(self.lyrics)
    grades = []
    affin_data = Afinn()
    sentiment = sentiment_analysis.SentimentAnalysisSpanish()
    for line in self.lyrics.split("\n"):
        first_del_pos = line.find("[")
        second_del_pos = line.find("]")
        final_line = line
        if first_del_pos != second_del_pos:
            final_line = line.replace(line[first_del_pos:second_del_pos + 1], "")
        if final_line:
            if self.language == "en":
                grades.append(affin_data.score(final_line))
            elif self.language == "es":
                grades.append(sentiment.sentiment(final_line))
        if len(grades) > 0:
            grades_sum = 0
            for i in grades:
                grades_sum += i
            self.sentiment_value = grades_sum / len(grades)
            if self.language == "en":
                if self.sentiment_value >= 0.15:
                    self.sentiment = "positive"
                elif self.sentiment_value < -0.15:
                    self.sentiment = "negative"
                else:
                    self.sentiment = "neutral"
            elif self.language == "es":
                if self.sentiment_value >= 0.55:
                    self.sentiment = "positive"
                elif self.sentiment_value < 0.35:
                    self.sentiment = "negative"
                else:
                    self.sentiment = "neutral"
            else:
                self.sentiment = "neutral"