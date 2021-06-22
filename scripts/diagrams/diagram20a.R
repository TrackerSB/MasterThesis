source("config.R")
library(lubridate)
dat <-
  read.csv(paste(generated_files_dir, "diagram20.csv", sep = ""))
print(dat)
dat <- within(dat, duration <- toTime(duration))
dat <- within(dat, durationSec <- (((hour(
  duration
) * 60)
+ minute(duration)) * 60)
+ second(duration))
print(head(dat))

diagram <- ggplot(data = dat,
                  aes(x = round, y = durationSec)) +
  geom_line() +
  geom_point() +
  scale_x_continuous(limits = c(1, 11), breaks = seq(0, 11, 1)) +
  scale_y_continuous(limits = c(0, 750)) +
  geom_smooth(method = "lm", fullrange = TRUE) +
  geom_segment(x = 1, xend = 11, y = 210, yend = 2310, color = "red") +
  labs(x = "#Tests", y = "Time [s]") +
  scale_color_manual(values = defaultColorSequence)
diagram