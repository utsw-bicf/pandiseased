import pytest

pytestmark = [pytest.mark.indexing]

@pytest.mark.parametrize('expected', [
    "# http://localhost/batch_hub/type=Experiment/hub.txt",
    "hub ENCODE_DCC_search",
    "shortLabel Hub (search:)",
    "longLabel ENCODE Data Coordination Center Data Hub",
    "genomesFile genomes.txt",
    "email encode-help@lists.stanford.edu"
])
def test_hub(testapp, index_workbook, expected):
    res = testapp.get("/batch_hub/type=Experiment/hub.txt")
    assert expected in res.text


@pytest.mark.parametrize('expected', [
    "genome mm9",
    "trackDb mm9/trackDb.txt",
    "genome hg38",
    "trackDb hg38/trackDb.txt",
    "genome hg19",
    "trackDb hg19/trackDb.txt",
])
def test_genomes(testapp, index_workbook, expected):
    res = testapp.get("/batch_hub/type=Experiment/genomes.txt")
    assert expected in res.text


@pytest.mark.parametrize('expected', [
    "track KCESR575ZXX",
    "compositeTrack on",
    "type bed 3",
    "longLabel Encyclopedia annotation of chromatin state for IMR-90 - KCESR575ZXX",
    "shortLabel chromatin state of IMR-90 KCESR575ZXX",
    "visibility full",
    "pennantIcon https://www.encodeproject.org/static/img/pennant-encode.png https://www.encodeproject.org/ \"This trackhub was automatically generated from the ENCODE files and metadata found at the ENCODE portal\"",
    "subGroup1 view Views aENHAN=Candidate_enhancers bPROMO=Candidate_promoters cSTATE=Chromatin_state hSTATE=HMM_predicted_chromatin_state sPKS=Peaks",
    "subGroup2 BS Biosample IMR4590=IMR-90",
    "subGroup3 EXP Experiment KCESR575ZXX=KCESR575ZXX",
    "subGroup4 REP Replicates pool=Pooled",
    "sortOrder BS=+ REP=+ view=+",
    "    track KCESR575ZXX_cSTATE_view",
    "    parent KCESR575ZXX on",
    "    view cSTATE",
    "    type bigBed",
    "    visibility dense",
    "        track KCEFF762DWI",
    "        parent KCESR575ZXX_cSTATE_view on",
    "        bigDataUrl /files/KCEFF762DWI/@@download/KCEFF762DWI.bigBed?proxy=true",
    "        longLabel Encyclopedia annotation of IMR-90 semi-automated genome annotation pool KCESR575ZXX - KCEFF762DWI",
    "        shortLabel pool saga",
    "        type bigBed",
    "        subGroups BS=IMR4590 EXP=KCESR575ZXX REP=pool view=cSTATE",
])
def test_dataset_trackDb(testapp, workbook, expected):
    res = testapp.get("/annotations/KCESR575ZXX/@@hub/hg19/trackDb.txt")
    assert expected in res.text


@pytest.mark.parametrize('expected', [
    "track chip",
    "compositeTrack on",
    "type bed 3",
    "longLabel Collection of ENCODE ChIP-seq experiments",
    "shortLabel ENCODE ChIP-seq",
    "visibility full",
    "html ChIP",
    "subGroup1 view Views aOIDR=Optimal_IDR_thresholded_peaks bIDRT=IDR_thresholded_peaks cCIDR=Conservative_IDR_thresholded_peaks dRPKS=Pseudoreplicated_IDR_thresholded_peaks ePKS=Peaks gSPV=Signal_p-value fFCOC=Fold_change_over_control hSIG=Signal",
    "subGroup2 BS Biosample GM12878=GM12878",
    "subGroup3 EXP Experiment KCESR000DZQ=KCESR000DZQ",
    "subGroup4 REP Replicates pool=Pooled",
    "subGroup5 TARG Targets EBF1=EBF1",
    "sortOrder BS=+ TARG=+ REP=+ view=+ EXP=+",
    "dimensions dimA=REP",
    "dimensionAchecked pool",
    "    track chip_bIDRT_view",
    "    parent chip on",
    "    view bIDRT",
    "    type bigNarrowPeak",
    "    visibility dense",
    "    spectrum on",
    "        track KCEFF003COS",
    "        parent chip_bIDRT_view on",
    "        bigDataUrl /files/KCEFF003COS/@@download/KCEFF003COS.bigBed?proxy=true",
    "        longLabel EBF1 TF ChIP-seq of GM12878 IDR thresholded peaks pool KCESR000DZQ - KCEFF003COS",
    "        shortLabel pool IDRt pk",
    "        type bigNarrowPeak",
    "        color 153,38,0",
    "        altColor 115,31,0",
    "        subGroups BS=GM12878 EXP=ENCSR000DZQ REP=pool TARG=EBF1 view=bIDRT",
])
def test_genomes(testapp, workbook, expected):
    res = testapp.get("/batch_hub/type=Experiment%2C%2caccession%3DKCESR000DZQ%2C%2caccession%3DKCESRENCSR575ZXX/hg19/trackDb.txt")
    assert expected in res.text


@pytest.mark.parametrize('expected', [
    ""
])
def test_fileset_files_trackDb(testapp, workbook, expected):
    res = testapp.get("/publication-data/KCESR727WCB/@@hub/hg19/trackDb.txt")
    assert expected in res.text


@pytest.mark.parametrize('expected', [
    "# Empty composite for KCESR000ACY.  It cannot be visualized at this time.",
])
def test_experiment_trackDb(testapp, workbook, expected):
    res = testapp.get("/experiments/KCESR000ACY/@@hub/trackDb.txt")
    assert expected in res.text


@pytest.mark.parametrize('expected', [
    "genome hg38",
    "trackDb hg38/trackDb.txt",
])
def test_genome_txt(testapp, index_workbook, expected):
    res = testapp.get("/batch_hub/type=Experiment&assembly=GRCh38/genomes.txt")
    assert expected in res.text

@pytest.mark.parametrize('expected', [
    "GRCh38",
    "hg19"
])
def test_assembly(testapp, workbook, expected):
    res = testapp.get("/experiments/KCESR000AEN/")
    assert expected in res.json['assembly']


@pytest.mark.parametrize('expected', [
    "/experiments/KCESR000AEN/@@hub/hub.txt",
])
def test_hub_field(testapp, workbook, expected):
    res = testapp.get("/experiments/KCESR000AEN/")
    assert expected in res.json['hub']


def test_visualize(submitter_testapp, index_workbook):
    expected = {
        'GRCh38': [
            "Ensembl",
            "UCSC",
        ],
        'hg19': [
            "UCSC"
        ]
    }
    res = submitter_testapp.get("/experiments/KCESR000AEN/")
    assert set(expected['GRCh38']) == set(res.json['visualize']['GRCh38']) and set(expected['hg19']) == set(res.json['visualize']['hg19'])
