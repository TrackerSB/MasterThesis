source("config.R")
library(dplyr)
dat <-
  read.csv(paste(generated_files_dir, "diagram16.csv", sep = ""))
dat <- anonymize(dat, "author")
dat <-
  within(dat, budget <- ifelse(budget == 10, "10 min", "30 min"))
print(head(dat))
dat <- dat %>%
  group_by(author, budget) %>%
  summarise(meanNum = mean(number),
            sdNum = sd(number))
print(head(dat))

diagram <- ggplot(data = dat,
                  aes(x = author,
                      y = meanNum,
                      fill = budget)) +
  geom_bar(position = position_dodge(), stat = "identity") +
  geom_errorbar(
    width = 0.2,
    position = position_dodge(.9),
    aes(ymax = meanNum + sdNum,
        ymin = meanNum - sdNum)
  ) +
  labs(x = "", y = "#Tests") +
  theme(legend.position = "bottom") +
  scale_fill_manual(values = defaultColorSequence)
diagram