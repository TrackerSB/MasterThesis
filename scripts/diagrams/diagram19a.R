source("config.R")
dat <-
  read.csv(paste(generated_files_dir, "diagram19.csv", sep = ""))

dat <- within(dat, numtests <- 0)
dat <- within(dat, numsucceeded <- 0)
for (r in 1:10) {
  roundElements <- dat[dat$round == r, ]
  dat <-
    within(dat, numtests <-
             ifelse(round == r, nrow(roundElements), numtests))
  succeededElements <-
    dat[dat$round == r & dat$result == "SUCCEEDED", ]
  dat <-
    within(dat, numsucceeded <-
             ifelse(round == r, nrow(succeededElements), numsucceeded))
}
print(head(dat))

diagram <- ggplot(data = dat,
                  aes(
                    x = numtests,
                    y = numsucceeded / numtests * 100,
                    color = factor(numnodes)
                  )) +
  geom_line() +
  geom_point() +
  labs(x = "#Tests", y = "succeeded [%]") +
  guides(color = guide_legend(title = "#SimNodes")) +
  scale_y_continuous(limits = c(0, 100)) +
  scale_color_manual(values = defaultColorSequence)
diagram