source("config.R")
library(dplyr)
library(tidyverse)
dat <-
  read.csv(paste(generated_files_dir, "diagram19.csv", sep = ""))
dat <- within(dat, round <- factor(round))
dat <-
  within(dat, numStarted <-
           as.numeric(toDatetime(as.character(levels(
             started
           )))))
dat <-
  within(dat, numFinished <-
           as.numeric(toDatetime(as.character(levels(
             finished
           )))))
dat <- within(dat, relStarted <- -1)
dat <- within(dat, relFinished <- -1)
for (r in 1:10) {
  minStarted <- min(dat[dat$round == r,]$numStarted)
  dat[dat$round == r,]$relStarted <-
    dat[dat$round == r,]$numStarted - minStarted
  dat[dat$round == r,]$relFinished <-
    dat[dat$round == r,]$numFinished - minStarted
}
dat$relStartedFac <- as.factor(dat$relStarted)

dat <- dat %>%
  group_by(round) %>%
  mutate(relStartedFac = fct_reorder(relStartedFac, relStarted))
dat <- within(dat, element <- -1)
for (r in 1:10) {
  dat <- dat %>%
    mutate(relStartedFac = fct_reorder(relStartedFac, relStarted)) %>%
    mutate(element = ifelse(round == r, 1:nrow(dat[round == r,]), element))
}
dat <- within(dat, yOffset <- element * 0.09)
print(head(dat))

diagram <- dat %>%
  ggplot(
    aes(
      x = relStarted,
      xend = relFinished,
      y = as.numeric(round) + yOffset,
      yend = as.numeric(round) + yOffset,
      color = round
    )
  ) +
  geom_segment() +
  scale_y_continuous(breaks = seq(1, 11, 1)) +
  labs(x = "Time [s]", y = "Round") +
  guides(color = guide_legend(title = "#Tests")) +
  scale_color_manual(values = defaultColorSequence) +
  geom_vline(xintercept = 600)
diagram