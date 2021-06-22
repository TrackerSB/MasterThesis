library(ggplot2)

generated_files_dir <- "../generatedData/"

# Define global configs
defaultColorSequence <-
  c(
    "#B25A00",
    "#FFBB76",
    "#FF9A34",
    "#0188B2",
    "#8BE3FF",
    "#B20300",
    "#FF7876",
    "#FF3834",
    "#01B239",
    "#8BFFB0",
    "#8C00B2",
    "#E176FF",
    "#D334FF",
    "#70B201",
    "#D4FF8B",
    "#000000",
    "#999999"
  )

# Multiple plot function
#
# ggplot objects can be passed in ..., or to plotlist (as a list of ggplot objects)
# - cols:   Number of columns in layout
# - layout: A matrix specifying the layout. If present, 'cols' is ignored.
#
# If the layout is something like matrix(c(1,2,3,3), nrow=2, byrow=TRUE),
# then plot 1 will go in the upper left, 2 will go in the upper right, and
# 3 will go all the way across the bottom.
#
multiplot <-
  function(...,
           plotlist = NULL,
           file,
           cols = 1,
           layout = NULL) {
    library(grid)
    
    # Make a list from the ... arguments and plotlist
    plots <- c(list(...), plotlist)
    
    numPlots = length(plots)
    
    # If layout is NULL, then use 'cols' to determine layout
    if (is.null(layout)) {
      # Make the panel
      # ncol: Number of columns of plots
      # nrow: Number of rows needed, calculated from # of cols
      layout <- matrix(seq(1, cols * ceiling(numPlots / cols)),
                       ncol = cols,
                       nrow = ceiling(numPlots / cols))
    }
    
    if (numPlots == 1) {
      print(plots[[1]])
      
    } else {
      # Set up the page
      grid.newpage()
      pushViewport(viewport(layout = grid.layout(nrow(layout), ncol(layout))))
      
      # Make each plot, in the correct location
      for (i in 1:numPlots) {
        # Get the i,j matrix positions of the regions that contain this subplot
        matchidx <- as.data.frame(which(layout == i, arr.ind = TRUE))
        
        print(plots[[i]],
              vp = viewport(
                layout.pos.row = matchidx$row,
                layout.pos.col = matchidx$col
              ))
      }
    }
  }

anonymize <-
  function(tab, col){
    tab[[col]] <- ifelse(
      tab[[col]] == "Reference AI",
      "A0",
      ifelse(
        tab[[col]] == "Vsevolod Tymofyeyev",
        "A1",
        ifelse(
          tab[[col]] == "Marco Landau",
          "A2",
          ifelse(
            tab[[col]] == "Reference Generator",
            "G0",
            ifelse(
              tab[[col]] == "Sebastian Vogl",
              "G1",
              ifelse(
                tab[[col]] == "Harish Swaminathan Gopal",
                "G2",
                ifelse(
                  tab[[col]] == "Sebastian Asen",
                  "G3",
                  "unknown"
                )
              )
            )
          )
        )
      )
    )
    return(tab)
  }

toTime <- function(timestring){
  return(as.POSIXct(timestring, format = "%H:%M:%S"))
}

toDatetime <- function(timestring){
  return(as.POSIXct(timestring, format = "%Y-%m-%d %H:%M:%S"))
}

dateDiff <- function(started, finished, units){
  return(difftime(
    toDatetime(finished),
    toDatetime(started),
    units = units
  ))
}