import logging


class DeriveName:
    def __init__(self):
        mrcc2 = "mitochondrial respiratory chain complex II"
        self.go_name_mapping = {
            "hemoglobin complex": "Hemoglobin complex",
            "proteasome core complex": "Proteasome core complex",
            "proteasome complex": "Proteasome complex",
            "myosin complex": "Myosin complex",
            "photosystem I": "Photosystem I",
            "photosystem II": "Photosystem II",
            "ATP synthesis coupled proton transport": "ATP synthase, complex V",
            "mitochondrial proton-transporting ATP synthase complex": "ATP synthase, complex V",
            "nucleosome": "Nucleosome, Histone",
            "respiratory chain complex IV": "Respiratory chain complex IV",
            mrcc2: "Mitochondrial respiratory chain complex II",
            # noqa: B950
        }
        self.sub_name_mapping = {
            "50S ribosomal protein": "50S ribosome subunit",
            "30S ribosomal protein": "30S ribosome subunit",
            "60S ribosomal protein": "60S ribosome subunit",
            "40S ribosomal protein": "40S ribosome subunit",
            "40S cytosolic small ribosomal subunit": "40S ribosome subunit",
            "33S ribosomal protein": "33S ribosome subunit",
            "28S ribosomal protein": "28S ribosome subunit, mitochondrial",
            # mammalian mitochondrial
            "39S ribosomal protein": "39S ribosome subunit, mitochondrial",
            # noqa: B950 # plant mitochondrial
            "54S ribosomal protein": "54S ribosome subunit, mitochondrial",
            # noqa: B950 # yeast mitochondrial
            "37S ribosomal protein": "37S ribosome subunit , mitochondrial",
            # noqa: B950 # yeast mitochondrial
        }
        self.combined_name = {
            ",".join(["30S ribosome subunit", "50S ribosome subunit"]): "70S ribosome",
            # bacterial ribosome
            "40S ribosome subunit,60S ribosome subunit": "80S eukaryotic ribosome",
            # eukaryotic ribosome
            ",".join(
                [
                    "28S ribosome subunit",
                    "mitochondrial,39S ribosome subunit",
                    "mitochondrial",
                ]
            ): "55S mammalian mitochondrial ribosome",
            # noqa: B950 # mammalian mitochondrial
            ",".join(
                ["33S ribosome subunit", "50S ribosome subunit"]
            ): "78S plant mitochondrial ribosome",
            # plant mitochondrial ribosome
            ",".join(
                [
                    "37S ribosome subunit",
                    "mitochondrial,54S ribosome subunit",
                    "mitochondrial",
                ]
            ): "74S yeast mitochondrial ribosome"
            # noqa: B950 # yeast mitochondrial
        }
        self.ribosome_go_terms = [
            "ribosome",
            "translation",
            "mitochondrial large ribosomal subunit",
            "large ribosomal subunit",
            "small ribosomal subunit",
            "structural constituent of ribosome",
        ]

        self.ribosomal_rna_accessions = [
            "RF00001",  # 5S ribosomal RNA
            "RF00002",  # 5.8S ribosomal RNA
            "RF00177",  # Bacterial small subunit ribosomal RNA
            "RF01959",  # Archaeal small subunit ribosomal RNA
            "RF01960",  # Eukaryotic small subunit ribosomal RNA
            "RF02540",  # Archaeal large subunit ribosomal RNA
            "RF02541",  # Bacterial large subunit ribosomal RNA
            "RF02542",  # Microsporidia small subunit ribosomal RNA
            "RF02543",  # Eukaryotic large subunit ribosomal RNA
            "RF02545",
            # Trypanosomatid mitochondrial small subunit ribosomal RNA
            "RF02546",
            # Trypanosomatid mitochondrial large subunit ribosomal RNA
        ]
        self.trna = ["RF00005", "RF01852"]  # tRNA  # selenocystine tRNA

    def get_name_from_go(self, go_list):
        """
        Returns GO complex name

        Args:
            go_list (list): list of GO terms

        Returns:
            string: GO name
        """
        for go_term in go_list:
            if go_term in self.go_name_mapping:
                return self.go_name_mapping[go_term]

        return None

    def has_ribosomal_rna(self, rna_accessions):
        """
        Return true if the accession matches any of the ribosome
        rfam accessions

        Args:
            rna_accessions (list): a list of accessions

        Returns:
            boolean: true if the accession matches any of the ribosome
            rfam accessions
        """
        for rna_accession in rna_accessions:
            if rna_accession in self.ribosomal_rna_accessions:
                return True
        return False

    def has_trna(self, rna_accessions):
        """
        Return true if the accession matches any of the tRNA
        rfam accessions

        Args:
            rna_accessions (list): a list of accessions

        Returns:
            boolean: true if the accession matches any of the tRNA
            rfam accessions
        """
        for rna_accession in rna_accessions:
            if rna_accession in self.trna:
                return True
        return False

    def get_name_from_names_for_ribosome(self, accession_dict, cut_off=5):
        """
        Returns ribosome derived name

        Args:
            accession_dict (dict): A dict of protein accessions and names
            cut_off (int, optional): Num of ribosomal proteins. Defaults to 5.

        Returns:
            string: ribosome name
        """
        logging.debug("starting test for derived name for ribosome")
        logging.debug(accession_dict.keys())
        derived_name = ""
        derived_names = set()
        found_names = set()
        missing_names = set()
        for accession in accession_dict:
            protein_name = accession_dict[accession].get("name")
            go_terms = accession_dict[accession].get("go_terms")
            if protein_name:
                for key in self.sub_name_mapping:
                    if key in protein_name:
                        test_derived_name = self.sub_name_mapping.get(key)
                        logging.debug(
                            'found name for "{}" - "{}"'.format(
                                protein_name, test_derived_name
                            )
                        )
                        derived_names.add(test_derived_name)
                        found_names.add(protein_name)
                        break
                if protein_name not in found_names:
                    is_ribosomal = False
                    if go_terms:
                        for go_term in go_terms:
                            if go_term in self.ribosome_go_terms:
                                is_ribosomal = True
                                break
                    if not is_ribosomal:
                        logging.debug("name missing {}".format(protein_name))
                        missing_names.add(protein_name)

        logging.debug("derived names")
        logging.debug(derived_names)
        logging.debug("num missing names: {}".format(len(missing_names)))
        if len(found_names) > cut_off:
            logging.debug("has over {} protein subunits".format(cut_off))
            if len(derived_names) > 1:
                derived_name_string = ",".join(sorted(list(derived_names)))
                logging.debug("derived name string: {}".format(derived_name_string))
                if derived_name_string in self.combined_name:
                    updated_name = self.combined_name.get(derived_name_string)
                    if updated_name:
                        logging.debug(updated_name)
                        derived_names = set()
                        derived_names.add(updated_name)
            logging.debug("derived names {}".format(derived_names))
            derived_name = ",".join(sorted(list(derived_names)))

            if missing_names:
                derived_name = "{} and {}".format(
                    derived_name, " and ".join(sorted(list(missing_names)))
                )

            logging.debug("final name: {}".format(derived_name))
        return derived_name
