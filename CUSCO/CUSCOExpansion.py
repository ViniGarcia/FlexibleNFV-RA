######## BRANCH CLASS DESCRIPTION ########

#PROJECT: NFV FLERAS (FLExible Resource Allocation Service)
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vfulber@inf.ufsm.br

#RECEIVES A BRANCH SEGMENT (LIST FORMAT) TO BE
#PROCESSED AND SEPARETED INTO LISTS. THIS CLASS
#ALSO DETECT AVAILABLE UNIONS ON THE BRANCHES.

#THE CLASS STATUS ATTRIBUTE INDICATE ITS
#OPERATIONS RESULTS CODES:

#NORMAL CODES ->
#0: NO BRANCH ANALYZED
#1: AVAILABLE ANALYZED BRANCH

#################################################

class Branch:
	__status = None
	__type = None

	__originalSegment = None
	__boundaryEPs = None
	__branchSegments = None
	__branchDependencies = None

	__beginMatches = None
	__beginMatchesInfra = None
	__beginMatchList = None
	__beginStringList = None

	__endMatches = None
	__endMatchesInfra = None
	__endMatchList = None
	__endStringList = None

	######## CONSTRUCTOR ########

	def __init__(self, branchSegment, boundaryEPs):

		if branchSegment == None or boundaryEPs == None:
			self.__status = 0
		else:
			self.bSetup(branchSegment, boundaryEPs)

	######## PRIVATE METHODS ########

	def __bSepareSegments(self):

		allSegments = []
		lastSegment = 0
		skipBrace = 0
		for index in range(len(self.__originalSegment)):
			if self.__originalSegment[index] == '{':
				skipBrace += 1
			if self.__originalSegment[index] == '}':
				skipBrace -= 1
			if self.__originalSegment[index] == '/':
				if skipBrace == 0:
					allSegments.append(self.__originalSegment[lastSegment:index])
					lastSegment = index + 1
		allSegments.append(self.__originalSegment[lastSegment:len(self.__originalSegment)])

		return allSegments

	def __bSepareDependencies(self):

		branchDependencies = []
		for bIndex in range(len(self.__branchSegments)):
			segmentDependencies = {}
			while '<' in self.__branchSegments[bIndex]:
				index = self.__branchSegments[bIndex].index('<')
				segmentDependencies[index-1] = self.__branchSegments[bIndex][index+1]
				self.__branchSegments[bIndex] = self.__branchSegments[bIndex][0:index] + self.__branchSegments[bIndex][index+3:len(self.__branchSegments[bIndex])]
			branchDependencies.append(segmentDependencies)

		return branchDependencies

	def __bNonTerminalBranch(self):

		for ep in self.__boundaryEPs:
			if ep in self.__originalSegment:
				return False

		return True

	def __bBeginMatchBranches(self):

		self.__beginMatches = 0
		self.__beginMatchesInfra = []

		minimumSize = len(self.__branchSegments[0])
		for segment in self.__branchSegments:
			if '{' in segment:
				size = len(segment) - (len(segment) - segment.index('{')) - 1
			else:
				size = len(segment) - 1

			if size == 0:
				return
			if size < minimumSize:
				minimumSize = size

		for index in range(minimumSize):
			analysis = -1
			dependency = False

			for sIndex in range(len(self.__branchSegments)):
				if analysis != -1:
					if analysis != self.__branchSegments[sIndex][index]:
						return
					if index in self.__branchDependencies[sIndex]:
						if dependency:
							if dependency != self.__branchDependencies[sIndex][index]:
								return
						else:
							dependency = self.__branchDependencies[sIndex][index]
				else:
					analysis = self.__branchSegments[sIndex][index]
					if index in self.__branchDependencies[sIndex]:
						dependency = self.__branchDependencies[sIndex][index]

			self.__beginMatches += 1
			self.__beginMatchesInfra.append(dependency)

	def __bBeginMergeMatches(self):

		self.__beginMatchList = []
		if self.__beginMatches == 0:
			return

		for bIndex in range(1, self.__beginMatches+1):
			allSegments = self.__bSepareSegments()

			branchMatch = []
			branchBase = []
			for index in range(bIndex):
				branchMatch.append(allSegments[0][index])
				if self.__beginMatchesInfra[index]:
					branchMatch.append('<')
					branchMatch.append(self.__beginMatchesInfra[index])
					branchMatch.append('>')

			branchBase.append('{')
			for subSegment in allSegments:
				for index in range(bIndex):
					if subSegment[1] == '<':
						subSegment = subSegment[4:]
					else:
						subSegment = subSegment[1:]
				branchBase += subSegment
				branchBase.append('/')

			branchBase.pop()
			branchBase.append('}')

			self.__beginMatchList.append((branchMatch, branchBase))

	def __bBeginStringMatches(self):

		self.__beginStringList = []

		originalBranch = self.__originalSegment.copy()
		originalBranch.insert(0, '{')
		originalBranch.append('}')
		self.__beginMatchList.append(([], originalBranch))
		for match in self.__beginMatchList:
			if match[0] != []:
				stringBranchMatch = [match[0][0]]
			else:
				stringBranchMatch = []
			for index in range(1, len(match[0])):
				stringBranchMatch.append(' ')
				stringBranchMatch.append(match[0][index])
			stringBaseMatch = [match[1][0]]
			for index in range(1, len(match[1])):
				stringBaseMatch.append(' ')
				stringBaseMatch.append(match[1][index])

			self.__beginStringList.append((''.join(stringBranchMatch), ''.join(stringBaseMatch)))

	def __bEndMatchBranches(self):

		self.__endMatches = 0
		self.__endMatchesInfra = []

		if not self.__type:
			return

		minimumSize = len(self.__branchSegments[0])
		for segment in self.__branchSegments:
			if '}' in segment:
				size = segment[::-1].index('}') - 1
			else:
				size = len(segment) - 1

			if size == 0:
				return
			if size < minimumSize:
				minimumSize = size

		for index in range(minimumSize):
			analysis = -1
			dependency = False

			for sIndex in range(len(self.__branchSegments)):
				eIndex = (len(self.__branchSegments[sIndex]) - 1) - index
				if analysis != -1:
					if analysis != self.__branchSegments[sIndex][eIndex]:
						return
					if eIndex in self.__branchDependencies[sIndex]:
						if dependency:
							if dependency != self.__branchDependencies[sIndex][eIndex]:
								return
						else:
							dependency = self.__branchDependencies[sIndex][eIndex]
				else:
					analysis = self.__branchSegments[sIndex][eIndex]
					if eIndex in self.__branchDependencies[sIndex]:
						dependency = self.__branchDependencies[sIndex][eIndex]

			self.__endMatches += 1
			self.__endMatchesInfra.append(dependency)

	def __bEndMergeMatches(self):

		self.__endMatchList = []
		if self.__endMatches == 0:
			return

		for bIndex in range(1, self.__endMatches+1):
			allSegments = self.__bSepareSegments()

			branchMatch = []
			branchBase = []
			modIndex = 0
			for index in range(bIndex):
				if self.__endMatchesInfra[index]:
					branchMatch.insert(0, '>')
					branchMatch.insert(0, self.__endMatchesInfra[index])
					branchMatch.insert(0, '<')
					modIndex += 3
				branchMatch.insert(0, allSegments[0][(len(allSegments[0]) - 1) - index - modIndex])

			branchBase.append('{')
			for subSegment in allSegments:
				for index in range(bIndex):
					if subSegment[-1] == '>':
						subSegment = subSegment[:len(subSegment)-4]
					else:
						subSegment = subSegment[:len(subSegment)-1]
				branchBase += subSegment
				branchBase.append('/')

			branchBase.pop()
			branchBase.append('}')

			self.__endMatchList.append((branchMatch, branchBase))

	def __bEndStringMatches(self):

		self.__endStringList = []
		if self.__endMatches == 0:
			return

		originalBranch = self.__originalSegment.copy()
		originalBranch.insert(0, '{')
		originalBranch.append('}')
		self.__endMatchList.append(([], originalBranch))
		for match in self.__endMatchList:
			if match[0] != []:
				stringBranchMatch = [match[0][0]]
			else:
				stringBranchMatch = []
			for index in range(1, len(match[0])):
				stringBranchMatch.append(' ')
				stringBranchMatch.append(match[0][index])
			stringBaseMatch = [match[1][0]]
			for index in range(1, len(match[1])):
				stringBaseMatch.append(' ')
				stringBaseMatch.append(match[1][index])

			self.__endStringList.append((''.join(stringBranchMatch), ''.join(stringBaseMatch)))

	######## PUBLIC METHODS ########

	def bSetup(self, originalSegment, boundaryEPs):

		self.__originalSegment = originalSegment
		self.__boundaryEPs = boundaryEPs
		self.__branchSegments = self.__bSepareSegments()
		self.__branchDependencies = self.__bSepareDependencies()
		self.__type = self.__bNonTerminalBranch()

		self.__status = 1

	def bAnalyzeBegin(self):

		if self.__status > 0:
			self.__bBeginMatchBranches()
			self.__bBeginMergeMatches()
			self.__bBeginStringMatches()

			if self.__status == 1:
				self.__status = 2
			else:
				self.__status = 4

	def bAnalyzeEnd(self):

		if self.__status > 0:
			self.__bEndMatchBranches()
			self.__bEndMergeMatches()
			self.__bEndStringMatches()

			if self.__status == 1:
				self.__status = 3
			else:
				self.__status = 4

	def bStatus(self):

		return self.__status

	def bBeginMatches(self):

		if self.__status != 2 and self.__status != 4:
			return None

		return self.__beginMatches

	def bBeginMatchList(self):

		if self.__status != 2 and self.__status != 4:
			return None

		return self.__beginMatchList

	def bBeginStringList(self):

		if self.__status != 2 and self.__status != 4:
			return None

		return self.__beginStringList

	def bEndMatches(self):

		if self.__status < 3:
			return None

		return self.__endMatches

	def bEndMatchList(self):

		if self.__status < 3:
			return None

		return self.__endMatchList

	def bEndStringList(self):

		if self.__status < 3:
			return None

		return self.__endStringList

######## BRANCH CLASS END ########


######## CUSCO EXPANSION CLASS DESCRIPTION ########

#PROJECT: NFV FLERAS (FLExible Resource Allocation Service)
#CREATED BY: VINICIUS FULBER GARCIA
#CONTACT: vfulber@inf.ufsm.br

#RECEIVES A VALID SFC TOPOLOGY AND EXPANDS
#ITS SPECIFIC STRUCTURES BY RESOLVING PARTIAL
#ORDERS AND MERGING BRANCHES. IT RETURNS ALL
#POSSIBLE COMBINATIONS.

#THE CLASS STATUS ATTRIBUTE INDICATE ITS
#OPERATIONS RESULTS CODES:

#NORMAL CODES ->
#0: NO TOPOLOGY EXPANDED
#1: AVAILABLE EXPANDED TOPOLOGIES

#ERROR CODES ->
#-1: RECEIVED TOPOLOGY IS NOT VALID
#-2: NO COMBINATION IS AVAILABLE FOR THE PARTIAL ORDER

#################################################

######## CUSCO EXPANSION CLASS BEGIN ########

import itertools

class CUSCOExpansion:
	__status = None

	__sfcTopology = None
	__sfcPOrder = None
	__sfcBranches = None

	######## CONSTRUCTOR ########

	def __init__(self, sfcTopology):

		if sfcTopology == None:
			self.__status = 0
		else:
			self.ceExpand(sfcTopology)

	######## PRIVATE METHODS ########

	def __ceStringfy(self, charList):

			stringData = [charList[0]]
			for index in range(1, len(charList)):
				stringData.append(' ')
				stringData.append(charList[index])

			return ''.join(stringData)

	def __ceValidatePermutation(self, permutation, oDependency, cDependency):

		for dependency in cDependency:
			if permutation.index(dependency[0]) != permutation.index(dependency[1])-1:
				return False

		for dependency in oDependency:
			if permutation.index(dependency[0]) > permutation.index(dependency[1]):
				return False

		return True

	def __ceCombinePermutations(self, pOrderSegments, sfcTopology):

		allPermutations = []
		for segment in pOrderSegments:
			allPermutations.append(segment.poCombinations())
		pOrderProduct = list(itertools.product(*allPermutations))

		sfcTopology = sfcTopology.split()
		key = 0

		while '[' in sfcTopology:
			index = sfcTopology.index('[')
			sfcTopology[index] = key
			sfcTopology = sfcTopology[0:index+1] + sfcTopology[sfcTopology.index(']')+1:len(sfcTopology)]
			key += 1
		while '(' in sfcTopology:
			sfcTopology = sfcTopology[0:sfcTopology.index('(')] + sfcTopology[sfcTopology.index(')')+1:len(sfcTopology)]

		allCombinations = []
		for hardOrdering in pOrderProduct:
			sfcAdapted = sfcTopology
			for index in range(key):
				sfcAdapted = sfcAdapted[0:sfcAdapted.index(index)] + list(hardOrdering[index]) + sfcAdapted[sfcAdapted.index(index)+1:len(sfcAdapted)]
			allCombinations.append(sfcAdapted)

		return allCombinations

	def __cePartialOrder(self):

		pOrderSegments = self.__sfcTopology.cPOrder()
		for segment in pOrderSegments:
			availablePermutations = list(itertools.permutations(segment.poElements()))
			acceptedPermutations = []

			for permutation in availablePermutations:
				if self.__ceValidatePermutation(permutation, segment.poODependencies(), segment.poCDependencies()):
					acceptedPermutations.append(list(permutation))

			if len(acceptedPermutations) == 0:
				self.__status = -2
				return None

			segment.poSetupCombinations(acceptedPermutations)

		return self.__ceCombinePermutations(pOrderSegments, self.__sfcTopology.cTopology())

	def __ceSeparateBranches(self, splittedSFC):

		sfcBranches = []

		for index in range(0, len(splittedSFC)):

			if splittedSFC[index] == '{':
				processIndex = index + 1
				jumpBraces = 0
				while True:
					if splittedSFC[processIndex] == '}':
						if jumpBraces == 0:
							sfcBranches.append(splittedSFC[index+1:processIndex])
							break
						else:
							jumpBraces -= 1
					if splittedSFC[processIndex] == '{':
						jumpBraces += 1
					processIndex += 1

		return sfcBranches

	def __ceRestructBranchBegin(self, base, combination):

		for cIndex in range(len(combination)):

			if combination[cIndex] == None:
				continue

			currentBranch = 0
			skipBrace = 0
			start = -1

			for index in range(len(base)):

				if base[index] == '{':
					if currentBranch == cIndex:
						start = index
					else:
						if start != -1:
							skipBrace += 1
					currentBranch += 1
					continue

				if base[index] == '}':
					if start != -1:
						if skipBrace != 0:
							skipBrace -= 1
						else:
							stop = index
							break

			if base[start-1][0] == '<' and base[start-1][-1] == '>':
				base = base[:start-2] + combination[cIndex][0] +  base[start-2:start] + combination[cIndex][1] + base[stop+1:]
			else:
				base = base[:start-1] + combination[cIndex][0] +  [base[start-1]] + combination[cIndex][1] + base[stop+1:]

		return base

	def __ceRestructBranchEnd(self, base, combination):

		nonTerminal = []
		boundaryEPs = self.__sfcTopology.cEPs()
		flag = True
		skip = 0

		index = 0
		while index < len(base):

			if base[index] == '{':
				if flag:
					start = index
					flag = False
				else:
					skip += 1
				index += 1
				continue

			if base[index] == '}':
				if not flag:
					if skip != 0:
						skip -= 1
					else:
						if not base[index-1] in boundaryEPs and not base[index-1] == '}':
							nonTerminal.append((start, index))
						index = start
						flag = True
			index += 1

		for cIndex in range(len(combination)):

			if combination[cIndex] == None:
				continue

			base = base[:nonTerminal[cIndex][0]] + combination[cIndex][1] + combination[cIndex][0] + base[nonTerminal[cIndex][1]+1:]

		return base

	def __ceBranches(self):

		bBranchTopologies = []
		for topology in self.__sfcPOrder:
			sfcBranches = self.__ceSeparateBranches(topology)
			branchesStructure = []

			for index in range(len(sfcBranches)):
				branchInstance = Branch(sfcBranches[index], self.__sfcTopology.cEPs())
				branchInstance.bAnalyzeBegin()

				if branchInstance.bBeginMatchList() != []:
					branchesStructure.append(branchInstance.bBeginMatchList())
				else:
					branchesStructure.append([None])

			combinationList = list(itertools.product(*branchesStructure))
			for combination in combinationList:
				bBranchTopologies.append(self.__ceRestructBranchBegin(topology, combination))

		availableTopologies = []
		for topology in bBranchTopologies:
			sfcBranches = self.__ceSeparateBranches(topology)
			branchesStructure = []

			if len(sfcBranches) == 0:
				availableTopologies.append(self.__ceStringfy(topology))
				continue

			for index in range(len(sfcBranches)):
				branchInstance = Branch(sfcBranches[index], self.__sfcTopology.cEPs())
				branchInstance.bAnalyzeEnd()

				if branchInstance.bEndMatchList() != []:
					branchesStructure.append(branchInstance.bEndMatchList())
				else:
					branchesStructure.append([None])

				combinationList = list(itertools.product(*branchesStructure))
				for combination in combinationList:
					availableTopologies.append(self.__ceStringfy(self.__ceRestructBranchEnd(topology, combination)))

		return availableTopologies

	######## PUBLIC METHODS ########

	def ceExpand(self, sfcTopology):

		self.__sfcTopology = sfcTopology
		if self.__sfcTopology.cStatus() != 1:
			self.__status = -1

		self.__sfcPOrder = self.__cePartialOrder()
		if self.__status == -2:
			return
		self.__sfcBranches = self.__ceBranches()

		self.__status = 1

	def ceStatus(self):

		return self.__status

	def cePOrder(self):

		if self.__status != 1:
			return None

		stringPOrders = []
		for pOrder in self.__sfcPOrder:
			stringPOrders.append(self.__ceStringfy(pOrder))

		return stringPOrders

	def ceBranches(self):

		if self.__status != 1:
			return None

		return self.__sfcBranches

######## CUSCO EXPANSION CLASS END ########
