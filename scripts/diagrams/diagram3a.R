source("config.R")
dat <-
  read.csv(paste(generated_files_dir, "diagram3.csv", sep = ""))
print(head(dat))

angleDiagram <-
  ggplot(data = dat, aes(x = author, y = initialcartolaneangle)) +
  geom_boxplot() +
  labs(x="", y="Initial car-to-road angle")
  scale_fill_manual(values = defaultColorSequence)

positionDiagram <-
  ggplot(
    data = within(dat, misplaced <- travelleddistance < 1),
    stat = "identity",
    aes(x = author, fill=misplaced)
  ) +
  geom_bar(position="fill") +
  labs(x = "", y = "") +
  scale_fill_manual(values = defaultColorSequence, labels = c("no", "yes"))

multiplot(angleDiagram, positionDiagram)