from typing import Optional, List, Tuple

class Node:
	def __init__(self, cidade: str):
		self.cidade: str = cidade
		self.left: Optional['Node'] = None
		self.right: Optional['Node'] = None

	def __repr__(self) -> str:
		return f"Node({self.cidade!r})"


class BinarySearchTree:
	def __init__(self):
		self.root: Optional[Node] = None

	def inserir(self, cidade: str) -> None:
		cidade = cidade.strip()
		if not cidade:
			return

		def _inserir(no: Optional[Node], cidade: str) -> Node:
			if no is None:
				return Node(cidade)
			# comparação case-insensitive, mas preserva o nome original
			if cidade.lower() < no.cidade.lower():
				no.left = _inserir(no.left, cidade)
			elif cidade.lower() > no.cidade.lower():
				no.right = _inserir(no.right, cidade)
			else:
				# já existe — não inserir duplicata
				pass
			return no

		self.root = _inserir(self.root, cidade)

	def buscar(self, cidade: str) -> bool:
		cidade = cidade.strip()
		no = self.root
		while no:
			if cidade.lower() == no.cidade.lower():
				return True
			elif cidade.lower() < no.cidade.lower():
				no = no.left
			else:
				no = no.right
		return False

	def remover(self, cidade: str) -> bool:
		cidade = cidade.strip()
		self.root, removed = self._remover_rec(self.root, cidade)
		return removed

	def _remover_rec(self, no: Optional[Node], cidade: str) -> Tuple[Optional[Node], bool]:
		if no is None:
			return None, False

		if cidade.lower() < no.cidade.lower():
			no.left, removed = self._remover_rec(no.left, cidade)
			return no, removed
		elif cidade.lower() > no.cidade.lower():
			no.right, removed = self._remover_rec(no.right, cidade)
			return no, removed
		else:
			# encontrado: três casos
			# caso 1: sem filhos
			if no.left is None and no.right is None:
				return None, True
			# caso 2: um filho
			if no.left is None:
				return no.right, True
			if no.right is None:
				return no.left, True
			# caso 3: dois filhos -> substituir pelo menor à direita
			successor = self._min_node(no.right)
			assert successor is not None
			no.cidade = successor.cidade
			no.right, _ = self._remover_rec(no.right, successor.cidade)
			return no, True

	def _min_node(self, no: Node) -> Node:
		while no.left:
			no = no.left
		return no

	def in_ordem(self) -> List[str]:
		res: List[str] = []

		def _in(no: Optional[Node]):
			if no is None:
				return
			_in(no.left)
			res.append(no.cidade)
			_in(no.right)

		_in(self.root)
		return res

	def pre_ordem(self) -> List[str]:
		res: List[str] = []

		def _pre(no: Optional[Node]):
			if no is None:
				return
			res.append(no.cidade)
			_pre(no.left)
			_pre(no.right)

		_pre(self.root)
		return res

	def pos_ordem(self) -> List[str]:
		res: List[str] = []

		def _pos(no: Optional[Node]):
			if no is None:
				return
			_pos(no.left)
			_pos(no.right)
			res.append(no.cidade)

		_pos(self.root)
		return res

	def contar_nos(self) -> int:
		def _contar(no: Optional[Node]) -> int:
			if no is None:
				return 0
			return 1 + _contar(no.left) + _contar(no.right)

		return _contar(self.root)

	def sugerir_por_prefixo(self, prefixo: str) -> List[str]:
		prefixo = prefixo.strip().lower()
		if not prefixo:
			return []
		matches: List[str] = []

		def _buscar(no: Optional[Node]):
			if no is None:
				return
			nome_lower = no.cidade.lower()
			# podar ramos: se o prefixo é menor que o nó atual, ir para esquerda
			if nome_lower.startswith(prefixo):
				matches.append(no.cidade)
				_buscar(no.left)
				_buscar(no.right)
			else:
				# decidir direção de busca por comparação lexicográfica
				if prefixo <= nome_lower:
					_buscar(no.left)
				else:
					_buscar(no.right)

		_buscar(self.root)
		return sorted(matches, key=lambda s: s.lower())

	def sugerir_por_similaridade(self, termo: str, max_results: int = 5, max_dist: Optional[int] = None) -> List[Tuple[str, int]]:
		termo = termo.strip().lower()
		if not termo:
			return []

		todos: List[str] = self.in_ordem()
		distances: List[Tuple[str, int]] = []
		for nome in todos:
			d = _levenshtein(termo, nome.lower())
			if max_dist is None or d <= max_dist:
				distances.append((nome, d))

		distances.sort(key=lambda x: (x[1], x[0].lower()))
		return distances[:max_results]


def _levenshtein(a: str, b: str) -> int:
	# implementação iterativa com memória O(min(len(a), len(b)))
	if a == b:
		return 0
	if len(a) == 0:
		return len(b)
	if len(b) == 0:
		return len(a)

	# garantir que b seja o menor para ter menos uso de memória
	if len(a) < len(b):
		a, b = b, a

	previous = list(range(len(b) + 1))
	for i, ca in enumerate(a, start=1):
		current = [i]
		for j, cb in enumerate(b, start=1):
			insertions = previous[j] + 1
			deletions = current[j - 1] + 1
			substitutions = previous[j - 1] + (0 if ca == cb else 1)
			current.append(min(insertions, deletions, substitutions))
		previous = current
	return previous[-1]

if __name__ == '__main__':
	# Demonstração simples
	arv = BinarySearchTree()
	cidades = [
		'São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Curitiba', 'Porto Alegre',
		'Florianópolis', 'Fortaleza', 'Salvador', 'Recife', 'Manaus', 'Belém', 'Goiânia'
	]

	for c in cidades:
		arv.inserir(c)

	print('In-ordem (alfabético):', arv.in_ordem())
	print('Pré-ordem:', arv.pre_ordem())
	print('Pós-ordem:', arv.pos_ordem())
	print('Total de nós:', arv.contar_nos())

	# buscas
	for consulta in ['Curitiba', 'Lisboa', 'belém']:
		print(f"Busca por '{consulta}':", arv.buscar(consulta))

	# remoção
	print('\nRemovendo Recife...')
	arv.remover('Recife')
	print('In-ordem depois da remoção:', arv.in_ordem())
	print('Total de nós:', arv.contar_nos())

	# sugestões por prefixo
	pref = 'Be'
	print(f"\nSugestões por prefixo '{pref}':", arv.sugerir_por_prefixo(pref))

	# sugestões por similaridade
	termo = 'Belm'
	print(f"Sugestões por similaridade para '{termo}':", arv.sugerir_por_similaridade(termo, max_results=5, max_dist=3))

