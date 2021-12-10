from itertools import zip_longest
from functools import total_ordering


@total_ordering
class Version:
    maturity_options = {
        0.25: ("sr", "service-release", "service_release"),
        -0.25: ("rc", "release-candidate", "release_candidate"),
        -0.5: ("b", "beta"),
        -0.75: ("a", "alpha"),
    }

    def __init__(self, version):
        self.version = version
        self.scraped_version = Version.scrape_numbers(self.version)

    def __eq__(self, other):
        other_scraped_version = Version.scrape_numbers(other.version)
        result = Version.compare_version_lists(self.scraped_version, other_scraped_version)
        return True if result == 0 else False

    def __lt__(self, other):
        version_other = Version.scrape_numbers(other.version)
        result = Version.compare_version_lists(self.scraped_version, version_other)
        return True if result < 0 else False

    @staticmethod
    def scrape_numbers(version: str) -> list:
        """
        Scrape off the value of each rank of the version

        The string is split into ranks by points. Reduce each rank to the number and
        add it to the list. If 'ValueError' raise try to scrape off the number and
        the name of the version maturity. Add the resulting number to the list.

        Parameters
        ----------
        version : str
            dot-separated values with maturity

        Returns
        -------
        number_list : list
            list of numbers corresponding to each rank of the version
        """
        number_list = []
        for rank in version.split("."):
            try:
                number_list.append(int(rank))
            except ValueError:
                number = Version.scrape_maturity(rank)
                number_list.append(number)
        return number_list

    @staticmethod
    def scrape_maturity(rank: str) -> int:
        """
        Scrape off the name of the maturity of the rank

        Itarate over characters and add them to 'raw_number' if it is a number,
        or to 'maturity' if it is a letter. The resulting number is reduced to 'int'.

        Parameters
        ----------
        rank : str
            rank of the version
        
        Returns
        -------
        number : int
            version rank value with maturity
        """
        raw_number = ""
        maturity = ""
        for c in rank:
            if c.isdigit():
                raw_number += c
            elif c.isalpha():
                maturity += c
        raw_number = int(raw_number) if raw_number else 0
        number = Version.apply_maturity(raw_number, maturity)
        return number
        
    @staticmethod
    def apply_maturity(raw_number: int, maturity: str) -> int:
        """
        Add the value corresponding to each maturity to the version rank     
        
        Parameters
        ----------
        raw_number : int
            the number of the corresponding version rank
        maturity : str
            the maturity of the corresponding version rank

        Raises
        ------
        ValueError
            failed to scrape version maturity

        Returns
        -------
        raw_number : int
            the sum of the rank value and the corresponding maturity value
        """
        for value, maturity_names in Version.maturity_options.items():
            if maturity in maturity_names:
                raw_number += value
                return raw_number
        else:
            raise ValueError("failed to process maturity")

    @staticmethod
    def compare_version_lists(version_self: list, version_other: list) -> int:
        """
        Compare the values of two lists sequentially

        Combine two lists using 'zip_longest' and compare the values.
        If the values are equal the next pair is compared. If the values are not
        equal, the diffrence between the first and second values is returned.
        If all pares are equal, return '0'.

        Parameters
        ----------
        version_self : str
            list of numbers of the first version
        version_other : str
            list of numbers of the second version

        Returns
        -------
        value : int
            diffrence if the pair values are not equal and '0' otherwise
        """
        comparison_list = zip_longest(version_self, version_other, fillvalue=0)
        for value_1, value_2 in comparison_list:
            if value_1 == value_2:
                continue
            else:
                return value_1 - value_2
        else:
            return 0


def main():
    to_test = [
        ("1.0.0", "2.0.0"),
        ("1.0.0", "1.42.0"),
        ("1.2.0", "1.2.42"),
        ("1.1.0-alpha", "1.2.0-alpha.1"),
        ("1.0.1b", "1.0.10-alpha.beta"),
        ("1.0.0-rc.1", "1.0.0"),
    ]

    for version_1, version_2 in to_test:
        assert Version(version_1) < Version(version_2), "le failed"
        assert Version(version_2) > Version(version_1), "ge failed"
        assert Version(version_2) != Version(version_1), "neq failed"


if __name__ == "__main__":
    main()
