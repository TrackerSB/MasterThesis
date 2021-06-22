source("config.R")
dat <-
  read.csv(paste(generated_files_dir, "diagram4.csv", sep = ""))
print(head(dat))

dat$result <- as.character(dat$result)
dat$result[dat$invalid == "True"] <- "invalid"
dat$result[dat$failed == "True"] <- "errored"
print(head(dat))

diagrams <- list()
authors <- levels(factor(dat$aiauthor))
for (author in authors) {
  if (author != "") {
    diagram <- ggplot(data = subset(dat, aiauthor == author),
                      aes(x = aiauthor, y = number, fill = result)) +
      geom_bar(stat = "identity", position = "fill") +
      coord_polar("y", start = 0) +
      labs(x = "", y = author) +
      theme(axis.text.y = element_blank()) +
      scale_fill_manual(values = defaultColorSequence)
    diagrams[[author]] <- diagram
  }
}

multiplot(plotlist = diagrams, cols = 2)