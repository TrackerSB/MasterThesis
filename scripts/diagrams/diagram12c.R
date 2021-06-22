source("diagram12.R")

dat <- within(dat, label <- ifelse(aierrored == "True", "ERRORED", label))
print(dat)

diagram <- ggplot(data = subset(dat, dat$aiauthor != "unknown"),
                  aes(x = aiauthor,
                      stat = "identity",
                      fill = label)) +
  geom_bar(position = position_dodge2(preserve = "single")) +
  labs(x = "", y = "#Tests") +
  theme(legend.position = "bottom") +
  scale_fill_manual(values = diagramColorScheme,
                    name = "Result:")
diagram