source("config.R")
library(dplyr)
dat <-
  read.csv(paste(generated_files_dir, "diagram17.csv", sep = ""))
dat <- anonymize(dat, "author")
dat <- within(dat, delta <- dateDiff(started, finished, "mins"))
dat <- dat %>%
  group_by(author) %>%
  summarise(meanTime = mean(delta),
            sdTime = sd(delta))
print(head(dat))

diagram <- ggplot(data = dat,
                  aes(x = author, y = meanTime, fill = author)) +
  geom_bar(stat = "identity") +
  geom_errorbar(aes(ymin = meanTime - sdTime,
                    ymax = meanTime + sdTime),
                width = .2) +
  labs(x = "", y = "Execution time [min]") +
  scale_fill_manual(values = defaultColorSequence, guide = FALSE)
diagram