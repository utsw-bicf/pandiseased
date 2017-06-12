from snovault import upgrade_step
# from .upgrade_data.analysis_step_5_to_6 import (
#    label_mapping,
#    status_mapping,
#    title_mapping,
#    major_version_mapping,
#    aliases_mapping
#)


@upgrade_step('analysis_step', '1', '2')
def analysis_step_1_2(value, system):
    # http://redmine.encodedcc.org/issues/2770

    input_mapping = {
        'align-star-pe-v-1-0-2': ['reads'],
        'align-star-pe-v-2-0-0': ['reads'],
        'align-star-se-v-1-0-2': ['reads'],
        'align-star-se-v-2-0-0': ['reads'],
        'index-star-v-1-0-1': ['genome reference', 'spike-in sequence', 'reference genes'],
        'index-star-v-2-0-0': ['genome reference', 'spike-in sequence', 'reference genes'],
        'index-rsem-v-1-0-1': ['genome reference', 'spike-in sequence', 'reference genes'],
        'index-tophat-v-1-0-0': ['genome reference', 'spike-in sequence', 'reference genes'],
        'quant-rsem-v-1-0-2': ['transcriptome alignments'],
        'stranded-signal-star-v-1-0-1': ['alignments'],
        'stranded-signal-star-v-2-0-0': ['alignments'],
        'unstranded-signal-star-v-1-0-1': ['alignments'],
        'unstranded-signal-star-v-2-0-0': ['alignments'],
        'align-tophat-pe-v-1-0-1': ['reads'],
        'align-tophat-se-v-1-0-1': ['reads']
    }
    output_mapping = {
        'align-star-pe-v-1-0-2': ['alignments'],
        'align-star-pe-v-2-0-0': ['alignments'],
        'align-star-se-v-1-0-2': ['alignments'],
        'align-star-se-v-2-0-0': ['alignments'],
        'index-star-v-1-0-1': ['genome index'],
        'index-star-v-2-0-0': ['genome index'],
        'index-rsem-v-1-0-1': ['genome index'],
        'index-tophat-v-1-0-0': ['genome index'],
        'quant-rsem-v-1-0-2': ['gene quantifications'],
        'stranded-signal-star-v-1-0-1': [
            'minus strand signal of multi-mapped reads',
            'plus strand signal of multi-mapped reads',
            'minus strand signal of unique reads',
            'plus strand signal of unique reads'
        ],
        'stranded-signal-star-v-2-0-0': [
            'minus strand signal of multi-mapped reads',
            'plus strand signal of multi-mapped reads',
            'minus strand signal of unique reads',
            'plus strand signal of unique reads'
        ],
        'unstranded-signal-star-v-1-0-1': [
            'signal of multi-mapped reads',
            'signal of unique reads'
        ],
        'unstranded-signal-star-v-2-0-0': [
            'signal of multi-mapped reads',
            'signal of unique reads'
        ],
        'align-tophat-pe-v-1-0-1': ['alignments'],
        'align-tophat-se-v-1-0-1': ['alignments']
    }

    value['input_file_types'] = input_mapping[value['name']]
    value['output_file_types'] = output_mapping[value['name']]


@upgrade_step('analysis_step', '2', '3')
def analysis_step_2_3(value, system):
    # http://redmine.encodedcc.org/issues/3019

    import re

    if 'output_file_types' in value:
        for i in range(0, len(value['output_file_types'])):
            string = value['output_file_types'][i]
            value['output_file_types'][i] = re.sub('multi-mapped', 'all', string)
    if 'input_file_types' in value:
        for i in range(0, len(value['input_file_types'])):
            string = value['input_file_types'][i]
            value['input_file_types'][i] = re.sub('multi-mapped', 'all', string)

    # http://redmine.encodedcc.org/issues/3074
    del value['software_versions']

    # http://redmine.encodedcc.org/issues/3074 note 16 and 3073
    if value.get('name') in ['lrna-se-star-alignment-step-v-2-0',
                            'lrna-pe-star-alignment-step-v-2-0',
                            'lrna-pe-star-stranded-signal-step-v-2-0',
                            'lrna-pe-star-stranded-signals-for-tophat-step-v-2-0',
                            'lrna-se-star-unstranded-signal-step-v-2-0',
                            'lrna-se-star-unstranded-signals-for-tophat-step-v-2-0',
                            'index-star-v-2-0',
                            'rampage-grit-peak-calling-step-v-1-1'
                            ]:
        value['status'] = 'deleted'

    if value.get('name') == 'lrna-pe-rsem-quantification-v-1':
        value['parents'] = ['ace7163c-563a-43d6-a86f-686405af167d', #/analysis-steps/lrna-pe-star-alignment-step-v-1/'
                            '9ca04da2-5ef7-4ba1-b78c-41dfc4be0c11'  #/analysis-steps/index-rsem-v-1-0/'
                            ]
    elif value.get('name') == 'lrna-se-rsem-quantification-step-v-1':
        value['parents'] = ['3cad3827-7f21-4f70-9cbc-e718b5529775', #/analysis-steps/lrna-se-star-alignment-step-v-1/',
                            '9ca04da2-5ef7-4ba1-b78c-41dfc4be0c11'  #/analysis-steps/index-rsem-v-1-0/'
                            ]


@upgrade_step('analysis_step', '3', '4')
def analysis_step_3_4(value, system):
    # http://redmine.encodedcc.org/issues/3063
    if 'analysis_step_types' in value:
        value['analysis_step_types'] = list(set(value['analysis_step_types']))

    if 'input_file_types' in value:
        value['input_file_types'] = list(set(value['input_file_types']))

    if 'output_file_types' in value:
        value['output_file_types'] = list(set(value['output_file_types']))

    if 'qa_stats_generated' in value:
        value['qa_stats_generated'] = list(set(value['qa_stats_generated']))

    if 'parents' in value:
        value['parents'] = list(set(value['parents']))

    if 'aliases' in value:
        value['aliases'] = list(set(value['aliases']))

    if 'documents' in value:
        value['documents'] = list(set(value['documents']))


@upgrade_step('analysis_step', '5', '6')
def analysis_step_5_6(value, system):
    # http://redmine.encodedcc.org/issues/4987

    label_mapping = {
        'f92fcf9a-db51-46d7-b694-d91d9a0bfffd':	'alignment-pooling-step',
        '33c5bca6-5338-45b9-b837-04441d4b582c':	'alignment-subsampling-step',
        'b3d14d58-0b8b-4444-bf7a-d189a05d1a87':	'atac-seq-alignment-step',
        'dfe8ba35-de3c-4082-815e-44f02cb61a11':	'atac-seq-peak-calling-step',
        'a03713ca-a312-4695-9825-54c66ffca779':	'atac-seq-peak-filtering-step',
        '2cd74fc9-39fe-45a5-ae0e-b67336563d32':	'atac-seq-region-calling-step',
        '030c105f-bcf9-4057-9b8b-e03ec2714ff6':	'atac-seq-region-filter-step',
        '62d7596e-355f-4c5d-a063-eca09386a32e': 'atac-seq-signal-gen-step',
        '44d38916-570b-4376-8d68-ca2c17c81cf1':	'bed-2-bigbed-step',
        '725c5155-e3b6-4ecc-9ecc-21f6ff5b041c':	'broad-frip-seq-cuffdiff-step',
        '5994fc85-2ea6-402e-b3d6-6846c90a63d7':	'broad-frip-seq-fastq-alignment-step',
        'd72eced7-ad33-4cdc-8767-5a5ccaeb674c':	'bwa-alignment-step',
        'c55d01bf-3ad9-40ef-a302-06fcdb7dc230':	'bwa-indexing-step',
        'f8c83c95-08ad-446a-822a-34cd1aec58e2':	'bwa-raw-alignment-step',
        '9c8db551-c458-4583-b1db-495ecd464e8f':	'celltype-cre-identification-step',
        '4c576ff1-c9fd-4c26-a340-1b5dce5afa91':	'chia-pet-chromatin-interactions-calling-step',
        '54e479a8-5d62-4a25-a959-82544578192f':	'chia-pet-haplotype-specific-step',
        'e132aa32-ec39-4954-9916-8ca752f3715a':	'chia-pet-loop-calling-step',
        'f8aae8a4-df4d-4456-9573-07611ed4ada0':	'chia-pet-peak-calling-step',
        '7eb14a04-460f-4a9d-a6de-6d77595b8fad':	'chia-pet-preprocessing-step',
        'bb86c2a6-f8b6-4b0c-9321-12650e41bce1':	'cluster-filter-step',
        '08fd0a3a-9d4f-483c-9316-e382da277344':	'control-alignment-subsampling-step',
        '8110ea62-6d65-4698-bf7a-09dceeeaecab':	'dac-enhancer-like-ranking-method-step',
        'c9421dc2-4b79-425d-9912-b85036916725':	'dac-promotor-like-ranking-method-step',
        '0caee7c2-71d0-428b-9033-05f5395ddbe1':	'deleted-dme-align-se-step',
        'fecdf1f3-6547-41f5-ae38-501437ef8357':	'deleted-dme-index-bismark-step',
        '359d63f3-8e92-4731-a719-58fb7053bdb9':	'deleted-lrna-index-star-step',
        '3fa67405-fa88-4627-b3eb-04f789eb5d29':	'deleted-lrna-pe-star-alignment-step',
        '8a78daa3-ef86-4203-acc0-a11d9c874697':	'deleted-lrna-pe-star-stranded-signal-step',
        '22dee925-30d9-4b01-ba3c-ea5cbfb15c98':	'deleted-lrna-pe-star-stranded-signals-for-tophat-step',
        '8eda9dfa-b9f1-4d58-9e80-535a5e4aaab1':	'deleted-lrna-se-star-alignment-step',
        '86070670-8998-4abe-82fc-96471701d6d4':	'deleted-lrna-se-star-unstranded-signal-step',
        '579e77ce-2594-42c1-82da-5f03ea2bb91b':	'deleted-lrna-se-star-unstranded-signals-for-tophat-step',
        'a40d988e-3545-47f9-874d-64cef2b87ea0':	'deleted-rampage-grit-peak-calling-step',
        '6ce8704b-783f-4b2a-bd21-72116b0f93dc':	'dme-align-pe-step',
        '36a667fe-e98c-402d-babf-88a9d39df5ff':	'dme-align-se-step',
        '1dbf4678-ba13-461f-bf6d-1ecbb6fd4b07':	'dme-extract-pe-step',
        '9476dd4e-24b9-4e8d-9317-4e57edffac8f':	'dme-extract-se-step',
        '6c421358-9065-4b37-b7e2-908228a23881':	'dme-index-bismark-bowtie1-step',
        '626fd29f-12f1-4f24-9ec7-8bb8de05024c':	'dme-index-bismark-bowtie2-step',
        '22aa0560-ddc2-4dfb-923d-4c6e7c26a91b':	'dme-rep-corr-pe-step',
        'd1bc159c-5d23-438a-b1d3-d1c9eb99c6a9':	'dme-rep-corr-se-step',
        '72c0c4a5-0e5c-4ff9-a835-e6b142c2b559':	'dnase-align-bwa-pe-step',
        '95657775-c775-4cd6-8f8a-1ec14bae48e6':	'dnase-align-bwa-se-step',
        '208715a1-1998-4191-9f00-16378333ccb1':	'dnase-bed-to-bigbed-step',
        'c6a9f81b-f9f7-49f3-9e09-7b36e21b4e19':	'dnase-call-hotspots-pe-step',
        'a1715ffe-7ec8-4a5f-a009-1e2fbd595dd7':	'dnase-call-hotspots-se-step',
        '243b3956-2b7a-4799-8122-2ed34c49d0c0':	'dnase-eval-bam-pe-step',
        'aaaa2291-ccaf-4633-bd7b-fef23abb9faa':	'dnase-eval-bam-se-step',
        '95876730-ad2a-46e2-ade5-408374bd8799':	'dnase-filter-pe-step',
        '44fa469b-16b8-4956-9bbc-094f6cc91c15':	'dnase-filter-se-step',
        '35f4e955-4e4f-4399-91ab-b80aba755d71':	'dnase-index-bwa-step',
        'd21d0aee-b6ff-4b72-99b1-a1837c471be1':	'dnase-rep-corr-pe-step',
        'e97f9afa-cb43-447b-800c-ba9f39142f02':	'dnase-rep-corr-se-step',
        'ff1f5989-1866-417e-a4b7-04879283cb3e':	'dnase-seq-mapping-peak-calling-step',
        '5dfa4f70-7c1c-4684-846d-4e823e584349':	'dnase-seq-mapping-step',
        '8a30a238-a240-49ca-ae33-476c2ed2f1b9':	'dnase-seq-peak-calling-step',
        '985f4d68-cb7e-4a43-8d5d-d3bdc01338da':	'eclip-bigbed-to-bed-step',
        '6dafd3a9-59b2-4625-843c-ea0ac27b3f6a':	'eclip-makebigwig-step',
        '8b75ec13-733c-47cb-9018-3130d36533eb':	'eclip-normalization-step',
        '49b998c5-d8bd-4d78-9fe9-d07182da99a9':	'eclip-trimming-mapping-step',
        'c23d0095-b46d-45ac-8ad2-7894ea627a04':	'encode2-dgf-analysis-step',
        'e064f272-2ad5-400d-b36e-f21ccb6b5a36':	'encode2-dnase-analysis-step',
        'defcb83d-fe1b-4c97-9ff2-7f53d7e9787b':	'generalized-cre-identification-step',
        '52a4c011-75da-48fc-99d8-878f6e1ace48':	'ggr-cl1-atac-seq-bam-to-bed-step',
        '6b60e60b-25ac-4e79-a634-c76927e0fafc':	'ggr-cl1-atac-seq-idr-step',
        '026793c1-b404-40ad-b270-073c281a9d4d':	'ggr-cl1-atac-seq-mapping-step',
        '3e449f3a-68d8-4751-90e9-b285192358e4':	'ggr-cl1-chip-seq-mapping-step',
        'af6d065f-2b10-4dd1-8168-d02209c715a5':	'ggr-cl1-chip-seq-quantification-step',
        '2dfa5e3a-8c6e-4f58-ba34-d300bfe24a1d':	'ggr-cl1-rna-seq-quantification-step',
        '4f7f108b-06ce-450a-8914-908ca3e8579a':	'ggr-cl1-rna-seq-trimming-mapping-filtering-step',
        '209ed0cb-c78f-44ee-b4ac-dee59affc5fe':	'ggr-lg1-atac-seq-bet-to-bigwig-step',
        '2467128f-c511-48d6-b9c4-6145ad492864':	'ggr-lg1-atac-seq-fastq-align-n-filter-step',
        'd6247a36-5ce9-410d-88d4-0ef3add91aa4':	'ggr-lg1-atac-seq-peak-calling-step',
        'd4511e7c-89f1-489f-a361-7ac34e4dfecc':	'ggr-lg1-chip-seq-bam-to-bigwig-step',
        '0903479b-3e8a-4617-b20e-29afaf558b2b':	'ggr-lg1-chip-seq-fastq-alignment-step',
        '8cdc02f8-be18-46da-a425-cc5f63fa634e':	'ggr-lg1-chip-seq-peak-calling-step',
        '6e284bc9-0b37-4adc-ac44-9710fe8314b9':	'ggr-lg1-rna-seq-bam2bigwig-step',
        '73df2227-9c93-4245-b799-c46ebcf19d2c':	'ggr-lg1-rna-seq-fastq-filtration-step',
        '846bb42a-06c7-4306-824d-9dbae9bed812':	'ggr-lg1-rna-seq-mapping-step',
        '2978ca0d-a8e6-4b92-8c2d-f4a09afd51b8':	'ggr-lg1-rna-seq-rsem-step',
        'acb8bee3-89c8-4d0c-bbaa-fb07d5ddd6f8':	'ggr-lg2-rna-seq-bam2bigwig-step',
        '401759ac-5d48-41c6-adb7-62d2376972d7':	'ggr-lg2-rna-seq-fastq-filtration-bowtie-step',
        'b731cb9c-f175-487f-8476-d9dd14770436':	'ggr-lg2-rna-seq-fastq-filtration-tophat-step',
        '5c27d324-dbe1-4b41-92d8-ed6d95fe32d5':	'ggr-lg2-rna-seq-rsem-step',
        '7697683d-5700-420c-bf98-7ff6ed98b254':	'ggr-tr1-chip-seq-mapping-filtering-step',
        'a632e947-a1f2-4f39-93d8-151174676de1':	'ggr-tr1-chip-seq-peak-calling-step',
        '16d3c366-c2c2-4b09-a658-0a64b2929f9a':	'ggr-tr1-chip-seq-quantification-step',
        '74c72ad9-2e76-4caf-b3d7-a818a7caf5e2':	'ggr-tr1-dnase-seq-mapping-filtering-step',
        '4ad61c77-ba1b-437c-880c-51b93a852c26':	'ggr-tr1-dnase-seq-peak-calling-step',
        '40a5a75d-0c23-4d6c-8cc0-c68d514a1b2c':	'ggr-tr1-dnase-seq-quantification-step',
        'a176ab91-b539-4f6f-a1ff-a74f8d45f806':	'ggr-tr1-hic-loop-calling-step',
        'a5575824-6427-4d25-930d-1b67550993b3':	'ggr-tr1-hic-mapping-step',
        'c1ffed71-6fa4-4aff-8641-51c38b8084d5':	'ggr-tr1-hic-tad-calling-step',
        '2fc04ec8-a808-4eb4-8df8-254368649f76':	'ggr-tr1-rna-seq-gene-quantification-step',
        '68a9926e-b340-4025-b00a-504fb9de6cdb':	'ggr-tr1-rna-seq-signal-generation-step',
        '6128d0c6-a76f-473f-b892-7e55238d43ed':	'ggr-tr1-rna-seq-trimming-mapping-step',
        'b401cd82-f452-4226-bf60-b90f9f45e2d6':	'hic-liftover-step',
        'ed93c57e-f2c1-486c-b713-53b6b5fb4a6b':	'histone-overlap-peaks-step',
        'e15f8dde-57a8-488e-a499-3d35eb6ccc03':	'histone-peak-calling-step',
        '0eefe557-2919-4dc9-8aff-379ecadf7bc8':	'histone-peaks-to-bigbed-step',
        '8c8a47de-a6ca-45a7-b2bf-08e6f6e70583':	'histone-replicated-peaks-to-bigbed-step',
        '576c8eee-6a76-47ec-93a0-a39601b719ee':	'histone-unreplicated-partition-concordance-peaks-to-bigbed-step',
        '19d3935a-fbca-4243-bb80-f61bc7333764':	'histone-unreplicated-partition-concordance-step',
        'e5fa3ff3-ff9b-4b42-a02f-a2eda0d3d06d':	'histone-unreplicated-peak-calling-step',
        '72d94ed9-cc29-495a-a697-6fd575f6f0ac':	'histone-unreplicated-peaks-to-bigbed-step',
        '426e37c9-ac4b-432b-ae7a-b7e0b198cb6f':	'kundaje-lab-atac-seq-filtered-peaks-conversion-single-rep-step',
        'bfcf57bf-55ac-42b6-ab0a-8f352fb0f784':	'kundaje-lab-atac-seq-filtered-peaks-conversion-step',
        '411131b3-32af-4179-94f2-03f067866ce4':	'kundaje-lab-atac-seq-idr-peaks-conversion-step',
        'cd3a15c3-fb7e-4ef2-a363-9096c990995a':	'kundaje-lab-atac-seq-idr-step',
        '48f52f6a-567e-4007-83d8-b5556c3e47f3':	'kundaje-lab-atac-seq-overlap-peaks-single-rep-step',
        '4fa087b8-f09f-4f3b-9130-9ca64a7fc457':	'kundaje-lab-atac-seq-overlap-peaks-step',
        '7bab42dc-0f83-4d9d-bdc1-ea501ea86507':	'kundaje-lab-atac-seq-peak-call-single-rep-step',
        '781d73ce-be94-49c9-b976-0ce0ee794c88':	'kundaje-lab-atac-seq-peak-call-step',
        '067e3432-f94d-4f2d-8da7-edf735cc17a4':	'kundaje-lab-atac-seq-pseudoreplicated-idr-peaks-conversion-single-rep-step',
        'a048867c-1ad5-4171-8fce-22f220b87d95':	'kundaje-lab-atac-seq-qc-single-rep-step',
        '6601935d-f10e-42eb-99ae-0ac87e62c73d':	'kundaje-lab-atac-seq-qc-step',
        'd5246641-23ff-4657-97ab-9dd2fedb58e2':	'kundaje-lab-atac-seq-replicated-peaks-conversion-step',
        '3e990eaa-8012-4a62-99ff-17c076366b7b':	'kundaje-lab-atac-seq-signals-single-rep-step',
        'c07180c7-9cd3-4c52-8a6f-b9b8002d618d':	'kundaje-lab-atac-seq-signals-step',
        'a2d34a26-a3fc-4a19-8e1a-5448b073a32f':	'kundaje-lab-atac-seq-stable-peaks-conversion-single-rep-step',
        '26d9c212-b06f-43ff-afb0-c4abdf5019c4':	'kundaje-lab-atac-seq-trim-align-filter-single-rep-step',
        '4800cf73-ef3c-4e6d-8ac4-8453fb60f315':	'kundaje-lab-atac-seq-trim-align-filter-step',
        '8ee938cc-5bb5-42ad-aee2-26f084931189':	'kundaje-lab-atac-seq-unreplicated-idr-single-rep-step',
        '9ca04da2-5ef7-4ba1-b78c-41dfc4be0c11':	'lrna-index-rsem-step',
        '76635694-c515-4a41-9976-ec59bb8b8522':	'lrna-index-star-step',
        '9e559b6e-c6f8-4ea7-9073-ec2d75af360f':	'lrna-index-tophat-step',
        'e33749d8-8680-4f0a-b1c3-5f58dcd9dc28':	'lrna-pe-rsem-quantification-step',
        'ace7163c-563a-43d6-a86f-686405af167d':	'lrna-pe-star-alignment-step',
        'b7c26c44-6c6a-4b13-a723-d09542516761':	'lrna-pe-star-signal-step',
        'bec07d6f-7283-4960-b04b-94819b5f69df':	'lrna-pe-star-signals-for-tophat-step',
        '8d7d13b4-a841-47d0-a7aa-ddf473f18e88':	'lrna-pe-tophat-alignment-step',
        'fa48d66e-0ff8-42ac-b051-474131abf3cf':	'lrna-repcorr-qc-pe-step',
        'd4e4b022-c242-4f70-a4d1-a09f50cdc84b':	'lrna-repcorr-qc-se-step',
        '7505ced9-3584-4146-84a1-7c5695cb8cf4':	'lrna-se-rsem-quantification-step',
        '3cad3827-7f21-4f70-9cbc-e718b5529775':	'lrna-se-star-alignment-step',
        '267a9410-348b-4f32-a1bf-9392aacb8f61':	'lrna-se-star-signal-step',
        '67dec549-0feb-493c-8b3c-830b34207076':	'lrna-se-star-signals-for-tophat-step',
        'd89fc557-a9a3-4a08-8bea-a92739380464':	'lrna-se-tophat-alignment-step',
        '6c81b297-e6cb-4890-a4e1-57fdb460bd6f':	'mango-align-bowtie-step',
        '763c29a3-424c-40e7-92e8-605b72bffd4a':	'mango-calc-interaction-confidence-step',
        'c50a624e-2774-4738-bc57-bb31c71665ae':	'mango-index-bowtie-step',
        'a87a2ff1-776b-4385-bf15-0bcce2d0cc0b':	'mango-macs2-call-peaks-step',
        '8940c5d1-eab6-436a-bd10-ed7c2b5bb9e1':	'mango-make-signal-step',
        'b2bb01ec-1093-4c00-97ec-209375202f07':	'mango-trim-linkers-step',
        '6cab4ead-7ae2-464a-903a-9d88725caf59':	'micro-rna-alignment-step',
        '85260ee8-4d73-4935-bbd2-9a2a491518ad':	'microrna-quantification-step',
        'd1886dde-6e31-4be7-88fe-734a435208e0':	'microrna-seq-alignment-step',
        '8254c900-fbe6-47ed-a26f-b0cd67143823':	'microrna-signal-step',
        '6981f3b6-73d6-43bf-8e44-eafcef8c90e1':	'modern-bwa-alignment-step',
        '6a02b98a-4478-419b-8a95-c79f6f3aa83f':	'modern-bwa-indexing-step',
        '09d087dc-832c-4d3f-afbe-e8a8ae92c4ae':	'modern-chip-seq-control-normalized-signal-generation-step',
        '70562049-b005-4ee6-926c-f47000365114':	'modern-chip-seq-filter-for-optimal-idr-peaks-step',
        '51607043-d15e-4214-8a0d-ef4f067f254c':	'modern-chip-seq-optimal-idr-step',
        '2de5fb71-af21-4ac8-95c8-59ff955ab29f':	'modern-chip-seq-optimal-idr-thresholded-peaks-to-bigbed-step',
        '72ffc094-afff-42c1-9bf9-0d6b8f335f9f':	'modern-chip-seq-peaks-to-bigbed-step',
        '0680d610-37f4-4289-a7d1-31a8414e1eaa':	'modern-chip-seq-read-depth-normalized-signal-generation-step',
        '9644e5d4-565b-4d42-bd23-9eb04e9e552a':	'modern-chip-seq-replicate-alignment-pooling-step',
        '2dd2b667-793a-48fb-8d2b-d979e71dfa22':	'modern-chip-seq-replicate-pooled-control-normalized-signal-generation-step',
        'ade8d389-2117-437b-843d-017358570e31':	'modern-chip-seq-replicate-pooled-read-depth-normalized-signal-generation-step',
        '379fa06f-1865-4b84-abe0-0a9f2f68b69f':	'modern-chip-seq-replicate-pooled-unique-read-signal-generation-step',
        '3d0dc233-9cd7-4396-9e3d-0208c75c6226':	'modern-chip-seq-spp-peak-calling-step',
        '6123cacb-1da9-4c30-b7de-9df8027dfa0c':	'modern-chip-seq-unique-read-signal-generation-step',
        'e7a0e1d6-ff93-403c-a74b-8d89fb5fccd7':	'modern-transcript-alignment-step',
        '0b205fcb-7b58-45fc-94e2-ca283971b06e':	'modern-transcript-quantification-step',
        '7c433f3f-9ff2-4011-821e-661b0fd0123b':	'nanostring-bigbed-step',
        '6dc5df87-a74e-4872-ab8c-37d3d607534a':	'nanostring-mapping-step',
        '62f17b52-9a51-47aa-bdc5-2658314860dd':	'nanostring-nsolver-step',
        'c5e72452-a392-4113-a674-5060857e427f':	'rampage-grit-peak-calling-step',
        'ac3a751d-486c-43a8-ab2f-35b74f40bc63':	'rampage-idr-step',
        'ee7d0f3d-5938-4413-a4e8-95e061933f68':	'rampage-pe-alignment-step',
        '7529ef1e-ca79-40e6-b4e8-a8a6444209ef':	'rampage-repcorr-qc-step',
        'e11a5798-37ae-4270-be7d-10c5fb9e9423':	'rampage-star-signal-step',
        '86c73c46-438a-488f-9fca-c4357ee7dbab':	'schatz-lab-variant-analysis-10x-longranger-align-call-phase-step',
        '1475bea2-da8b-40a6-aa26-52fd2368c800':	'schatz-lab-variant-analysis-10x-longranger-index-step',
        'cfe45ca1-2b22-4eb8-b390-83e4198aeb32':	'schatz-lab-variant-analysis-10x-longranger-phased-diploid-genome-step',
        '21599a32-5624-44f4-b940-3d5dbdf3f033':	'schatz-lab-variant-analysis-10x-vcf2diploid-phased-diploid-genome-step',
        'e1adc1cb-712a-48f6-bc1d-b3e6bc21a79b':	'schatz-lab-variant-analysis-gatk-indel-filtering-step',
        'e319306d-7c7f-45cc-9a8e-90cf869b4495':	'schatz-lab-variant-analysis-gatk-snp-filtering-step',
        '98d99189-0160-4d55-8cfd-c5287da2c3dc':	'schatz-lab-variant-analysis-gatk-variant-calling-step',
        '64950482-e5f9-4d33-af8b-d0d8d52a7bf9':	'schatz-lab-variant-analysis-scalpel-filtering-step',
        'aa5dcc5b-4c1e-426c-9e11-eabe9a372475':	'schatz-lab-variant-analysis-scalpel-variant-calling-step',
        '4eb7ff39-c894-4ea6-bff2-8874ec21811f':	'schatz-lab-variant-analysis-trim-bwa-mem-align-filter-step',
        '274aa669-2c83-42cc-9bac-4aa62fcf85c6':	'schatz-lab-variant-analysis-trim-ngm-align-filter-step',
        'e8e4b418-0048-4b9f-b250-a9b97a16710e':	'shrna-rna-seq-map-step',
        '1ede083b-9220-4ee3-aca4-bf691f70e23e':	'shrna-rna-seq-signal-step',
        'aa58b736-b5da-4e55-b448-b8011c7532bf':	'shrna-rna-splice-quant-step',
        'bbc283fc-4cd5-4374-a521-0d2ab609ef71':	'small-rna-repcorr-qc-step',
        'c5c03291-30eb-4bf7-a7b6-cd2e05a1afb4':	'small-rna-se-star-alignment-step',
        'c45c68cb-ed6f-40d8-b5d1-a0bec7313421':	'small-rna-star-indexing-step',
        '74e12aa7-3a71-491f-9bd3-731094cec3db':	'small-rna-star-stranded-signal-step',
        'c590043a-3bb1-403c-bc4b-67740aa8cb6b':	'tf-idr-peaks-to-bigbed-step',
        '0c3377fe-a83e-46d5-b548-d7e0669dde1a':	'tf-idr-step',
        '7c02066c-da5f-4316-8492-cd70419284b3':	'tf-macs2-signal-calling-step',
        '7b8e4925-6401-4737-8043-7722e81a02ee':	'tf-peaks-to-bigbed-step',
        '7a74345f-f75f-49e5-9001-eca3d3dfdc64':	'tf-spp-peak-calling-step',
        '123a9667-abb2-442a-93ed-3715c67534ea':	'tf-unreplicated-idr-peaks-to-bigbed-step',
        '19dec341-2dd2-45aa-a9ad-48dd035a8cf0':	'tf-unreplicated-idr-step',
        '66a8b2f3-8ff4-4965-a028-4379675bfabe':	'tf-unreplicated-macs2-signal-calling-step',
        'ca6a1673-c0a0-482a-bc2d-783d04685289':	'tf-unreplicated-peaks-to-bigbed-step',
        '0666fb66-35e4-4f67-a0a4-55f884cc6942':	'tf-unreplicated-spp-peak-calling-step',
        '59491001-082a-403e-b6c4-d991df0dd019':	'wgbs-bismark-quantification-step',
        '87f77826-78d4-4c38-bb92-ab1f933bb921':	'wgbs-methylation-to-bigbed-conversion-step'
    }

    major_version_mapping = {
        'f92fcf9a-db51-46d7-b694-d91d9a0bfffd':	1,
        '33c5bca6-5338-45b9-b837-04441d4b582c':	1,
        'b3d14d58-0b8b-4444-bf7a-d189a05d1a87':	1,
        'dfe8ba35-de3c-4082-815e-44f02cb61a11':	1,
        'a03713ca-a312-4695-9825-54c66ffca779':	1,
        '2cd74fc9-39fe-45a5-ae0e-b67336563d32':	1,
        '030c105f-bcf9-4057-9b8b-e03ec2714ff6':	1,
        '62d7596e-355f-4c5d-a063-eca09386a32e':	1,
        '44d38916-570b-4376-8d68-ca2c17c81cf1':	1,
        '725c5155-e3b6-4ecc-9ecc-21f6ff5b041c':	1,
        '5994fc85-2ea6-402e-b3d6-6846c90a63d7':	1,
        'd72eced7-ad33-4cdc-8767-5a5ccaeb674c':	1,
        'c55d01bf-3ad9-40ef-a302-06fcdb7dc230':	1,
        'f8c83c95-08ad-446a-822a-34cd1aec58e2':	1,
        '9c8db551-c458-4583-b1db-495ecd464e8f':	1,
        '4c576ff1-c9fd-4c26-a340-1b5dce5afa91':	1,
        '54e479a8-5d62-4a25-a959-82544578192f':	1,
        'e132aa32-ec39-4954-9916-8ca752f3715a':	1,
        'f8aae8a4-df4d-4456-9573-07611ed4ada0':	1,
        '7eb14a04-460f-4a9d-a6de-6d77595b8fad':	1,
        'bb86c2a6-f8b6-4b0c-9321-12650e41bce1':	1,
        '08fd0a3a-9d4f-483c-9316-e382da277344':	1,
        '8110ea62-6d65-4698-bf7a-09dceeeaecab':	1,
        'c9421dc2-4b79-425d-9912-b85036916725':	1,
        '0caee7c2-71d0-428b-9033-05f5395ddbe1':	2,
        'fecdf1f3-6547-41f5-ae38-501437ef8357':	2,
        '359d63f3-8e92-4731-a719-58fb7053bdb9':	2,
        '3fa67405-fa88-4627-b3eb-04f789eb5d29':	2,
        '8a78daa3-ef86-4203-acc0-a11d9c874697':	2,
        '22dee925-30d9-4b01-ba3c-ea5cbfb15c98':	2,
        '8eda9dfa-b9f1-4d58-9e80-535a5e4aaab1':	2,
        '86070670-8998-4abe-82fc-96471701d6d4':	2,
        '579e77ce-2594-42c1-82da-5f03ea2bb91b':	2,
        'a40d988e-3545-47f9-874d-64cef2b87ea0':	1,
        '6ce8704b-783f-4b2a-bd21-72116b0f93dc':	1,
        '36a667fe-e98c-402d-babf-88a9d39df5ff':	1,
        '1dbf4678-ba13-461f-bf6d-1ecbb6fd4b07':	1,
        '9476dd4e-24b9-4e8d-9317-4e57edffac8f':	1,
        '6c421358-9065-4b37-b7e2-908228a23881':	1,
        '626fd29f-12f1-4f24-9ec7-8bb8de05024c':	1,
        '22aa0560-ddc2-4dfb-923d-4c6e7c26a91b':	1,
        'd1bc159c-5d23-438a-b1d3-d1c9eb99c6a9':	1,
        '72c0c4a5-0e5c-4ff9-a835-e6b142c2b559':	1,
        '95657775-c775-4cd6-8f8a-1ec14bae48e6':	1,
        '208715a1-1998-4191-9f00-16378333ccb1':	1,
        'c6a9f81b-f9f7-49f3-9e09-7b36e21b4e19':	1,
        'a1715ffe-7ec8-4a5f-a009-1e2fbd595dd7':	1,
        '243b3956-2b7a-4799-8122-2ed34c49d0c0':	1,
        'aaaa2291-ccaf-4633-bd7b-fef23abb9faa':	1,
        '95876730-ad2a-46e2-ade5-408374bd8799':	1,
        '44fa469b-16b8-4956-9bbc-094f6cc91c15':	1,
        '35f4e955-4e4f-4399-91ab-b80aba755d71':	1,
        'd21d0aee-b6ff-4b72-99b1-a1837c471be1':	1,
        'e97f9afa-cb43-447b-800c-ba9f39142f02':	1,
        'ff1f5989-1866-417e-a4b7-04879283cb3e':	1,
        '5dfa4f70-7c1c-4684-846d-4e823e584349':	2,
        '8a30a238-a240-49ca-ae33-476c2ed2f1b9':	2,
        '985f4d68-cb7e-4a43-8d5d-d3bdc01338da':	1,
        '6dafd3a9-59b2-4625-843c-ea0ac27b3f6a':	1,
        '8b75ec13-733c-47cb-9018-3130d36533eb':	1,
        '49b998c5-d8bd-4d78-9fe9-d07182da99a9':	1,
        'c23d0095-b46d-45ac-8ad2-7894ea627a04':	1,
        'e064f272-2ad5-400d-b36e-f21ccb6b5a36':	1,
        'defcb83d-fe1b-4c97-9ff2-7f53d7e9787b':	1,
        '52a4c011-75da-48fc-99d8-878f6e1ace48':	1,
        '6b60e60b-25ac-4e79-a634-c76927e0fafc':	1,
        '026793c1-b404-40ad-b270-073c281a9d4d':	1,
        '3e449f3a-68d8-4751-90e9-b285192358e4':	1,
        'af6d065f-2b10-4dd1-8168-d02209c715a5':	1,
        '2dfa5e3a-8c6e-4f58-ba34-d300bfe24a1d':	1,
        '4f7f108b-06ce-450a-8914-908ca3e8579a':	1,
        '209ed0cb-c78f-44ee-b4ac-dee59affc5fe':	1,
        '2467128f-c511-48d6-b9c4-6145ad492864':	1,
        'd6247a36-5ce9-410d-88d4-0ef3add91aa4':	1,
        'd4511e7c-89f1-489f-a361-7ac34e4dfecc':	1,
        '0903479b-3e8a-4617-b20e-29afaf558b2b':	1,
        '8cdc02f8-be18-46da-a425-cc5f63fa634e':	1,
        '6e284bc9-0b37-4adc-ac44-9710fe8314b9':	1,
        '73df2227-9c93-4245-b799-c46ebcf19d2c':	1,
        '846bb42a-06c7-4306-824d-9dbae9bed812':	1,
        '2978ca0d-a8e6-4b92-8c2d-f4a09afd51b8':	1,
        'acb8bee3-89c8-4d0c-bbaa-fb07d5ddd6f8':	1,
        '401759ac-5d48-41c6-adb7-62d2376972d7':	1,
        'b731cb9c-f175-487f-8476-d9dd14770436':	1,
        '5c27d324-dbe1-4b41-92d8-ed6d95fe32d5':	1,
        '7697683d-5700-420c-bf98-7ff6ed98b254':	1,
        'a632e947-a1f2-4f39-93d8-151174676de1':	1,
        '16d3c366-c2c2-4b09-a658-0a64b2929f9a':	1,
        '74c72ad9-2e76-4caf-b3d7-a818a7caf5e2':	1,
        '4ad61c77-ba1b-437c-880c-51b93a852c26':	1,
        '40a5a75d-0c23-4d6c-8cc0-c68d514a1b2c':	1,
        'a176ab91-b539-4f6f-a1ff-a74f8d45f806':	1,
        'a5575824-6427-4d25-930d-1b67550993b3':	1,
        'c1ffed71-6fa4-4aff-8641-51c38b8084d5':	1,
        '2fc04ec8-a808-4eb4-8df8-254368649f76':	1,
        '68a9926e-b340-4025-b00a-504fb9de6cdb':	1,
        '6128d0c6-a76f-473f-b892-7e55238d43ed':	1,
        'b401cd82-f452-4226-bf60-b90f9f45e2d6':	1,
        'ed93c57e-f2c1-486c-b713-53b6b5fb4a6b':	1,
        'e15f8dde-57a8-488e-a499-3d35eb6ccc03':	1,
        '0eefe557-2919-4dc9-8aff-379ecadf7bc8':	1,
        '8c8a47de-a6ca-45a7-b2bf-08e6f6e70583':	1,
        '576c8eee-6a76-47ec-93a0-a39601b719ee':	1,
        '19d3935a-fbca-4243-bb80-f61bc7333764':	1,
        'e5fa3ff3-ff9b-4b42-a02f-a2eda0d3d06d':	1,
        '72d94ed9-cc29-495a-a697-6fd575f6f0ac':	1,
        '426e37c9-ac4b-432b-ae7a-b7e0b198cb6f':	1,
        'bfcf57bf-55ac-42b6-ab0a-8f352fb0f784':	1,
        '411131b3-32af-4179-94f2-03f067866ce4':	1,
        'cd3a15c3-fb7e-4ef2-a363-9096c990995a':	1,
        '48f52f6a-567e-4007-83d8-b5556c3e47f3':	1,
        '4fa087b8-f09f-4f3b-9130-9ca64a7fc457':	1,
        '7bab42dc-0f83-4d9d-bdc1-ea501ea86507':	1,
        '781d73ce-be94-49c9-b976-0ce0ee794c88':	1,
        '067e3432-f94d-4f2d-8da7-edf735cc17a4':	1,
        'a048867c-1ad5-4171-8fce-22f220b87d95':	1,
        '6601935d-f10e-42eb-99ae-0ac87e62c73d':	1,
        'd5246641-23ff-4657-97ab-9dd2fedb58e2':	1,
        '3e990eaa-8012-4a62-99ff-17c076366b7b':	1,
        'c07180c7-9cd3-4c52-8a6f-b9b8002d618d':	1,
        'a2d34a26-a3fc-4a19-8e1a-5448b073a32f':	1,
        '26d9c212-b06f-43ff-afb0-c4abdf5019c4':	1,
        '4800cf73-ef3c-4e6d-8ac4-8453fb60f315':	1,
        '8ee938cc-5bb5-42ad-aee2-26f084931189':	1,
        '9ca04da2-5ef7-4ba1-b78c-41dfc4be0c11':	1,
        '76635694-c515-4a41-9976-ec59bb8b8522':	1,
        '9e559b6e-c6f8-4ea7-9073-ec2d75af360f':	1,
        'e33749d8-8680-4f0a-b1c3-5f58dcd9dc28':	1,
        'ace7163c-563a-43d6-a86f-686405af167d':	1,
        'b7c26c44-6c6a-4b13-a723-d09542516761':	1,
        'bec07d6f-7283-4960-b04b-94819b5f69df':	1,
        '8d7d13b4-a841-47d0-a7aa-ddf473f18e88':	1,
        'fa48d66e-0ff8-42ac-b051-474131abf3cf':	1,
        'd4e4b022-c242-4f70-a4d1-a09f50cdc84b':	1,
        '7505ced9-3584-4146-84a1-7c5695cb8cf4':	1,
        '3cad3827-7f21-4f70-9cbc-e718b5529775':	1,
        '267a9410-348b-4f32-a1bf-9392aacb8f61':	1,
        '67dec549-0feb-493c-8b3c-830b34207076':	1,
        'd89fc557-a9a3-4a08-8bea-a92739380464':	1,
        '6c81b297-e6cb-4890-a4e1-57fdb460bd6f':	1,
        '763c29a3-424c-40e7-92e8-605b72bffd4a':	1,
        'c50a624e-2774-4738-bc57-bb31c71665ae':	1,
        'a87a2ff1-776b-4385-bf15-0bcce2d0cc0b':	1,
        '8940c5d1-eab6-436a-bd10-ed7c2b5bb9e1':	1,
        'b2bb01ec-1093-4c00-97ec-209375202f07':	1,
        '6cab4ead-7ae2-464a-903a-9d88725caf59':	1,
        '85260ee8-4d73-4935-bbd2-9a2a491518ad':	1,
        'd1886dde-6e31-4be7-88fe-734a435208e0':	1,
        '8254c900-fbe6-47ed-a26f-b0cd67143823':	1,
        '6981f3b6-73d6-43bf-8e44-eafcef8c90e1':	1,
        '6a02b98a-4478-419b-8a95-c79f6f3aa83f':	1,
        '09d087dc-832c-4d3f-afbe-e8a8ae92c4ae':	1,
        '70562049-b005-4ee6-926c-f47000365114':	1,
        '51607043-d15e-4214-8a0d-ef4f067f254c':	1,
        '2de5fb71-af21-4ac8-95c8-59ff955ab29f':	1,
        '72ffc094-afff-42c1-9bf9-0d6b8f335f9f':	1,
        '0680d610-37f4-4289-a7d1-31a8414e1eaa':	1,
        '9644e5d4-565b-4d42-bd23-9eb04e9e552a':	1,
        '2dd2b667-793a-48fb-8d2b-d979e71dfa22':	1,
        'ade8d389-2117-437b-843d-017358570e31':	1,
        '379fa06f-1865-4b84-abe0-0a9f2f68b69f':	1,
        '3d0dc233-9cd7-4396-9e3d-0208c75c6226':	1,
        '6123cacb-1da9-4c30-b7de-9df8027dfa0c':	1,
        'e7a0e1d6-ff93-403c-a74b-8d89fb5fccd7':	1,
        '0b205fcb-7b58-45fc-94e2-ca283971b06e':	1,
        '7c433f3f-9ff2-4011-821e-661b0fd0123b':	1,
        '6dc5df87-a74e-4872-ab8c-37d3d607534a':	1,
        '62f17b52-9a51-47aa-bdc5-2658314860dd':	1,
        'c5e72452-a392-4113-a674-5060857e427f':	1,
        'ac3a751d-486c-43a8-ab2f-35b74f40bc63':	1,
        'ee7d0f3d-5938-4413-a4e8-95e061933f68':	1,
        '7529ef1e-ca79-40e6-b4e8-a8a6444209ef':	1,
        'e11a5798-37ae-4270-be7d-10c5fb9e9423':	1,
        '86c73c46-438a-488f-9fca-c4357ee7dbab':	1,
        '1475bea2-da8b-40a6-aa26-52fd2368c800':	1,
        'cfe45ca1-2b22-4eb8-b390-83e4198aeb32':	1,
        '21599a32-5624-44f4-b940-3d5dbdf3f033':	1,
        'e1adc1cb-712a-48f6-bc1d-b3e6bc21a79b':	1,
        'e319306d-7c7f-45cc-9a8e-90cf869b4495':	1,
        '98d99189-0160-4d55-8cfd-c5287da2c3dc':	1,
        '64950482-e5f9-4d33-af8b-d0d8d52a7bf9':	1,
        'aa5dcc5b-4c1e-426c-9e11-eabe9a372475':	1,
        '4eb7ff39-c894-4ea6-bff2-8874ec21811f':	1,
        '274aa669-2c83-42cc-9bac-4aa62fcf85c6':	1,
        'e8e4b418-0048-4b9f-b250-a9b97a16710e':	1,
        '1ede083b-9220-4ee3-aca4-bf691f70e23e':	1,
        'aa58b736-b5da-4e55-b448-b8011c7532bf':	1,
        'bbc283fc-4cd5-4374-a521-0d2ab609ef71':	1,
        'c5c03291-30eb-4bf7-a7b6-cd2e05a1afb4':	1,
        'c45c68cb-ed6f-40d8-b5d1-a0bec7313421':	1,
        '74e12aa7-3a71-491f-9bd3-731094cec3db':	1,
        'c590043a-3bb1-403c-bc4b-67740aa8cb6b':	1,
        '0c3377fe-a83e-46d5-b548-d7e0669dde1a':	1,
        '7c02066c-da5f-4316-8492-cd70419284b3':	1,
        '7b8e4925-6401-4737-8043-7722e81a02ee':	1,
        '7a74345f-f75f-49e5-9001-eca3d3dfdc64':	1,
        '123a9667-abb2-442a-93ed-3715c67534ea':	1,
        '19dec341-2dd2-45aa-a9ad-48dd035a8cf0':	1,
        '66a8b2f3-8ff4-4965-a028-4379675bfabe':	1,
        'ca6a1673-c0a0-482a-bc2d-783d04685289':	1,
        '0666fb66-35e4-4f67-a0a4-55f884cc6942':	1,
        '59491001-082a-403e-b6c4-d991df0dd019':	1,
        '87f77826-78d4-4c38-bb92-ab1f933bb921': 1
    }

    title_mapping = {
        'fecdf1f3-6547-41f5-ae38-501437ef8357':	'WGBS Bismark-bowtie1 genome indexing step - Version 2',
        '3fa67405-fa88-4627-b3eb-04f789eb5d29':	'Long RNA-seq STAR paired-ended alignment step v2.0',
        '8eda9dfa-b9f1-4d58-9e80-535a5e4aaab1':	'Long RNA-seq STAR single-ended alignment step v2.0',
        '626fd29f-12f1-4f24-9ec7-8bb8de05024c':	'WGBS Bismark-bowtie2 genome indexing step - Version 1',
        'ff1f5989-1866-417e-a4b7-04879283cb3e':	'DNase-seq mapping and peak calling step'
    }

    status_mapping = {
        'f92fcf9a-db51-46d7-b694-d91d9a0bfffd': 'released',
        '33c5bca6-5338-45b9-b837-04441d4b582c': 'released',
        '9476dd4e-24b9-4e8d-9317-4e57edffac8f': 'released',
        'd1bc159c-5d23-438a-b1d3-d1c9eb99c6a9': 'released',
        '22aa0560-ddc2-4dfb-923d-4c6e7c26a91b': 'released',
        '70562049-b005-4ee6-926c-f47000365114': 'released',
        '2de5fb71-af21-4ac8-95c8-59ff955ab29f': 'released'
    }

    aliases_mapping = {
        'f92fcf9a-db51-46d7-b694-d91d9a0bfffd': 'encode:alignment-pooling-step-v-1',
        '33c5bca6-5338-45b9-b837-04441d4b582c': 'encode:alignment-subsampling-step-v-1',
        '5994fc85-2ea6-402e-b3d6-6846c90a63d7': 'encode:frip-seq-pipeline-alignment-step-v-1',
        '08fd0a3a-9d4f-483c-9316-e382da277344': 'encode:control-alignment-subsampling-step-v-1',
        '8110ea62-6d65-4698-bf7a-09dceeeaecab': 'zhiping-weng:dac-enhancer-like-ranking-method-step-v-1',
        'c9421dc2-4b79-425d-9912-b85036916725': 'zhiping-weng:dac-promoter-like-ranking-method-step-v-1',
        'fecdf1f3-6547-41f5-ae38-501437ef8357': 'dnanexus:deleted-dme-index-bismark-step-v-2',
        '208715a1-1998-4191-9f00-16378333ccb1': 'john-stamatoyannopoulos:dnase-bed-to-bigbed-v-1',
        'ff1f5989-1866-417e-a4b7-04879283cb3e': 'john-stamatoyannopoulos:dnase-seq-mapping-peak-calling-step-v-1',
        '5dfa4f70-7c1c-4684-846d-4e823e584349': 'john-stamatoyannopoulos:dnase-seq-mapping-step-v-2',
        '8a30a238-a240-49ca-ae33-476c2ed2f1b9': 'john-stamatoyannopoulos:dnase-seq-peak-calling-step-v-2',
        '6dafd3a9-59b2-4625-843c-ea0ac27b3f6a': 'gene-yeo:eclip-makebigwig-step-v-1',
        'c23d0095-b46d-45ac-8ad2-7894ea627a04': 'john-stamatoyannopoulos:encode2-dgf-analysis',
        'e064f272-2ad5-400d-b36e-f21ccb6b5a36': 'john-stamatoyannopoulos:encode2-dnase-analysis',
        'b401cd82-f452-4226-bf60-b90f9f45e2d6': 'zhiping-weng:hic-liftover-step-v-1',
        '359d63f3-8e92-4731-a719-58fb7053bdb9': 'encoded:deleted-lrna-index-star-v-2',
        '3fa67405-fa88-4627-b3eb-04f789eb5d29': 'encode:deleted-lrna-pe-star-alignment-step-v-2',
        '8a78daa3-ef86-4203-acc0-a11d9c874697': 'encode:deleted-lrna-pe-star-stranded-signal-step-v-2',
        '22dee925-30d9-4b01-ba3c-ea5cbfb15c98': 'encode:deleted-lrna-pe-star-stranded-signals-for-tophat-step-v-2',
        '8eda9dfa-b9f1-4d58-9e80-535a5e4aaab1': 'encode:deleted-lrna-se-star-alignment-step-v-2',
        '86070670-8998-4abe-82fc-96471701d6d4': 'encode:deleted-lrna-se-star-unstranded-signal-step-v-2',
        '579e77ce-2594-42c1-82da-5f03ea2bb91b': 'encode:deleted-lrna-se-star-unstranded-signals-for-tophat-step-v-2',
        '6cab4ead-7ae2-464a-903a-9d88725caf59': 'ali-mortazavi:micro-rna-alignment-step-v-1',
        '6dc5df87-a74e-4872-ab8c-37d3d607534a': 'ali-mortazavi:nanostring-mapping-step-v-1',
        'a40d988e-3545-47f9-874d-64cef2b87ea0': 'encode:deleted-rampage-grit-peak-calling-step-v-1',
        'e8e4b418-0048-4b9f-b250-a9b97a16710e': 'encode:shrna-rna-seq-map-step-v-1',
        '1ede083b-9220-4ee3-aca4-bf691f70e23e': 'encode:shrna-rna-seq-signal-step-v-1',
        'aa58b736-b5da-4e55-b448-b8011c7532bf': 'encode:shrna-rna-splice-quant-step-v-1'
    }

    uuid = value.get('uuid')

    value.update({'step_label': label_mapping[uuid]})
    value.update({'major_version': major_version_mapping[uuid]})
    if uuid in title_mapping:
        value.update({'title': title_mapping.get(uuid)})
    if uuid in status_mapping:
        value.update({'status': status_mapping.get(uuid)})
    if uuid in aliases_mapping:
        if 'aliases' not in value:
            value['aliases'] = []
        value['aliases'].append(aliases_mapping.get(uuid))
