normalise_to_spikes <- function(spikes, all_fpkms, plotname, outfile, track)
{
  ## remove spikes with zero fpkm, add 1, log 10 transform

  goodSpikes <- spikes[spikes$FPKM!=0,]
  
  copies = log10(goodSpikes$copies_per_cell + 1)
  fpkms = log10(goodSpikes$FPKM + 1 )

  ##get fit
  fit = lm(copies ~ 0 + fpkms + I(fpkms^2), list(copies,fpkms))

  #make diagnostic plot of fit.
  pdf(plotname)
  plot(log10(spikes$FPKM+1),log10(spikes$copies_per_cell+1),
       main=track,
       xlab="Spike in FPKM + 1 (log10)",
       ylab="Spike in copy number + 1 (log10)")
  plot_data = data.frame(fpkms=sort(log10(spikes$FPKM+1)))
  lines(plot_data$fpkms,predict(fit,plot_data),col="red")
  dev.off()

  #calculate copies per cell from the raw fpkms
  cufflinks_fpkms = data.frame(fpkms=log10(all_fpkms$FPKM+1), gene_id=all_fpkms$gene_id)

  transformed_copy_number = predict(fit,cufflinks_fpkms)

  copy_number = 10^transformed_copy_number - 1
  raw_fpkms = 10^cufflinks_fpkms$fpkms - 1

  normalised = data.frame(gene_id = cufflinks_fpkms$gene_id,
                          copy_number=copy_number,
                          FPKM = raw_fpkms)

  write.table(normalised, outfile, row.names=F,sep="\t",quote=F)

}

  
  
  
